import json
import datetime
import uuid
from collections import defaultdict
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum, Max
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from locksmith.common import get_signature, PUB_STATUSES, UNPUBLISHED
from locksmith.hub.models import Api, Key, KeyForm, Report, ResendForm, resolve_model
from locksmith.hub.tasks import push_key
from locksmith.hub.common import cycle_generator
from django.db.models import Sum

@require_POST
def report_calls(request):
    '''
        POST endpoint for APIs to report their statistics

        requires parameters: api, key, calls, date, endpoint & signature

        if 'api' or 'key' parameter is invalid returns a 404
        if signature is bad returns a 400
        returns a 200 with content 'OK' if call succeeds
    '''
    api_obj = get_object_or_404(Api, name=request.POST['api'])

    # check the signature
    if get_signature(request.POST, api_obj.signing_key) != request.POST['signature']:
        return HttpResponseBadRequest('bad signature')

    key_obj = get_object_or_404(Key, key=request.POST['key'])

    calls = int(request.POST['calls'])
    try:
        # use get_or_create to update unique #calls for (date,api,key,endpoint)
        report,c = Report.objects.get_or_create(date=request.POST['date'],
                                                api=api_obj,
                                                key=key_obj,
                                                endpoint=request.POST['endpoint'],
                                                defaults={'calls':calls})
        if not c:
            report.calls = calls
            report.save()
    except Exception, e:
        raise

    return HttpResponse('OK')

@require_POST
def reset_keys(request):
    '''
        POST endpoint to reset API keys for a given API
        (triggering a request for new keys)
    '''
    api_obj = get_object_or_404(Api, name=request.POST['api'])

    # check the signature
    if get_signature(request.POST, api_obj.signing_key) != request.POST['signature']:
        return HttpResponseBadRequest('bad signature')

    api_obj.pub_statuses.update(status=UNPUBLISHED)
    for key in Key.objects.all():
        push_key.delay(key)

    return HttpResponse('OK')


def register(request,
             email_template='locksmith/registration_email.txt',
             registration_template='locksmith/register.html',
             registered_template='locksmith/registered.html',
            ):
    '''
        API registration view

        displays/validates form and sends email on successful submission
    '''
    if request.method == 'POST':
        form = KeyForm(request.POST)
        if form.is_valid():
            newkey = form.save(commit=False)
            newkey.key = uuid.uuid4().hex
            newkey.status = 'U'
            newkey.save()

            send_key_email(newkey, email_template)
            return render_to_response(registered_template, {'key': newkey},
                                      context_instance=RequestContext(request))
    else:
        form = KeyForm()
    return render_to_response(registration_template, {'form':form},
                              context_instance=RequestContext(request))

def send_key_email(key, email_template):
    email_msg = render_to_string(email_template, {'key': key})
    email_subject = getattr(settings, 'LOCKSMITH_EMAIL_SUBJECT',
                            'API Registration')
    send_mail(email_subject, email_msg, settings.DEFAULT_FROM_EMAIL,
              [key.email])


def resend(request,
           reg_email_template='locksmith/registration_email.txt',
           resend_email_template='locksmith/resend_email.txt',
           resend_template='locksmith/resend.html',
          ):
    resp = {}

    if request.method == 'POST':
        form = ResendForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                key = Key.objects.get(email=email)
                if key.status == 'U':
                    send_key_email(key, reg_email_template)
                else:
                    send_key_email(key, resend_email_template)
                resp['key'] = key
            except Key.DoesNotExist:
                resp['nokey'] = True
        resp['form'] = form
    else:
        resp['form'] = ResendForm()

    return render(request, resend_template, resp)


def confirm_registration(request, key, template="locksmith/confirmed.html"):
    '''
        API key confirmation

        visiting this URL marks a Key as ready for use
    '''
    context = {}
    try:
        context['key'] = key_obj = Key.objects.get(key=key)
        if key_obj.status != 'U':
            context['error'] = 'Key Already Activated'
        else:
            key_obj.status = 'A'
            key_obj.mark_for_update()
            key_obj.save()
    except Key.DoesNotExist:
        context['error'] = 'Invalid Key'
    return render_to_response(template, context,
                              context_instance=RequestContext(request))


@login_required
def profile(request):
    '''
        Viewing of signup details and editing of password
    '''
    context = {}

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Password Changed.')
    else:
        form = PasswordChangeForm(request.user)

    key = Key.objects.get(email=request.user.email)
    
    #analytics
    endpoint_q = key.reports.values('api__name', 'endpoint').annotate(calls=Sum('calls')).order_by('-calls')
    endpoints = [{'endpoint':'.'.join((d['api__name'], d['endpoint'])),
                  'calls': d['calls']} for d in endpoint_q]
    date_q = key.reports.values('date').annotate(calls=Sum('calls')).order_by('date')
    context['endpoints'], context['endpoint_calls'] = _dictlist_to_lists(endpoints, 'endpoint', 'calls')
    context['timeline'] = date_q

    context['form'] = form
    context['key'] = key
    context['password_is_key'] = request.user.check_password(key.key)
    return render_to_response('locksmith/profile.html', context,
                              context_instance=RequestContext(request))

# analytics utils

def _dictlist_to_lists(dl, *keys):
    ''' convert a list of dictionaries to a dictionary of lists

    >>> dl = [{'a': 'test', 'b': 3}, {'a': 'zaz', 'b': 444},
              {'a': 'wow', 'b': 300}]
    >>> _dictlist_to_lists(dl)
    (['test', 'zaz', 'wow'], [3, 444, 300])
    '''
    lists = []
    for k in keys:
        lists.append([])
    for item in dl:
        for i, key in enumerate(keys):
            x = item[key]
            if isinstance(x, unicode):
                x = str(x)
            lists[i].append(x)
    return lists

def _cumulative_by_date(model, datefield):
    '''
        Given a model and date field, generate monthly cumulative totals.
    '''
    monthly_counts = defaultdict(int)
    for obj in model.objects.all().order_by(datefield):
        datevalue = getattr(obj, datefield)
        monthkey = (datevalue.year, datevalue.month)
        monthly_counts[monthkey] += 1

    if len(monthly_counts) == 0:
        return []

    earliest_month = min(monthly_counts.iterkeys())
    latest_month = max(monthly_counts.iterkeys())
    
    accumulator = 0 
    cumulative_counts = []
    for (year, month) in cycle_generator(cycle=(1, 12), begin=earliest_month, end=latest_month):
        mcount = monthly_counts.get((year, month), 0)
        accumulator += mcount
        cumulative_counts.append([datetime.date(year, month, 1), accumulator])

    return cumulative_counts

# analytics views -- all require staff permission

staff_required = user_passes_test(lambda u: u.is_staff)

@staff_required
def analytics_index(request,
                        keys_issued_display='chart', keys_issued_interval='yearly',
                        api_calls_display='chart'):
    ignore_internal_keys = request.GET.get('ignore_internal_keys', True)
    ignore_deprecated_apis = request.GET.get('ignore_deprecated_apis', True)
    ignore_inactive_keys = request.GET.get('ignore_inactive_keys', True)

    new_users = Key.objects.filter(issued_on__gte=(datetime.datetime.today()+datetime.timedelta(days=-14))).order_by('-issued_on')

    six_month = Key.objects.filter(issued_on__gte=(datetime.datetime.today()+datetime.timedelta(days=-4, weeks=-24)), issued_on__lte=(datetime.datetime.today()+datetime.timedelta(days=3, weeks=-24))).order_by('-issued_on')
    six_month_stats = []

    for sm in six_month:
        six_month_stats.append((sm, Report.objects.filter(key_id=sm.id).aggregate(Sum('calls'))['calls__sum'] ))

    six_month = sorted(six_month_stats, key=lambda tup: tup[1], reverse=True)

    apis = Api.objects.order_by('display_name') 

    options = {
        'ignore_internal_keys': ignore_internal_keys,
        'ignore_deprecated_apis': ignore_deprecated_apis,
        'ignore_inactive_keys': ignore_inactive_keys,
        'api_calls_display': api_calls_display,
        'keys_issued_display': keys_issued_display,
        'keys_issued_interval': keys_issued_interval
    }
    ctx = {
        'options': options,
        'json_options': json.dumps(options),
        'new_users': new_users,
        'six_month': six_month,
        'apis': apis,
    }
    return render(request, 'locksmith/analytics_index.html', ctx)

@staff_required
def api_analytics(request,
                      api_calls_display='chart', api_calls_interval='yearly',
                      api_id=None, api_name=None):
    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    ignore_internal_keys = request.GET.get('ignore_internal_keys', True)

    options = {
        'api': { 'id': api.id, 'name': api.name },
        'ignore_internal_keys': ignore_internal_keys,
        'api_calls_display': api_calls_display,
        'api_calls_interval': api_calls_interval
    }
    ctx = {
        'api': api,
        'options': options,
        'json_options': json.dumps(options),
    }
    return render(request, 'locksmith/api_analytics.html', ctx)

@staff_required
def key_list(request):
    options = {
    }
    ctx = {
        'options': options,
        'json_options': json.dumps(options),
    }
    return render(request, "locksmith/keys_list.html", ctx)

@login_required
def key_analytics(request, key):
    key = get_object_or_404(Key, key=key)

    if request.user.email != key.email and request.user.is_staff != True:
        return render(request, 'locksmith/key_analytics_unauthorized.html')

    ctx = {
        'key': key.key,
        'pub_statuses': [{'api': {'name': kps.api.name},
                          'status': kps.status,
                          'status_label': PUB_STATUSES[kps.status][1]}
                         for kps in key.pub_statuses.filter(api__push_enabled=True)],
        'endpoint_calls_display': 'chart',
        'api_calls_display': 'chart',
        'api_calls_interval': 'yearly'
    }
    ctx['json_options'] = json.dumps(ctx)
    ctx['key'] = key
    return render(request, 'locksmith/key_analytics.html', ctx)


@staff_required
def keys_leaderboard(request,
                     year=None, month=None,
                     api_id=None, api_name=None):
    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        api = None

    if year is not None and month is not None:
        year = int(year)
        month = int(month)
        if month not in range(1, 13):
            return HttpResponseBadRequest("Month must be between 1 and 12, was {m}".format(m=unicode(month)))
    else:
        year = datetime.date.today().year
        month = datetime.date.today().month

    ctx = {
        'latest_qtr_begin': datetime.datetime(year, month, 1).strftime('%Y-%m-%d')
    }
    if api is not None:
        ctx['api'] = {'id': api.id, 'name': api.name}
    ctx['json_options'] = json.dumps(ctx)
    return render(request, 'locksmith/leaderboard.html', ctx)

