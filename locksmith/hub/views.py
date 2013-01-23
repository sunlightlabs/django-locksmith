import json
import datetime
import uuid
from collections import defaultdict
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum, Max
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from locksmith.common import get_signature, UNPUBLISHED
from locksmith.hub.models import Api, Key, KeyForm, Report, ResendForm
from locksmith.hub.tasks import push_key


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

def _cycle_generator(cycle, step=1, begin=(0, 0), end=None):
    '''
        Generates pairs of values representing a cycle. E.g. clock hours for a day could
        could be generated with:
            _cycle_generator(cycle=(1, 12), step=1, begin=(0, 1), end=(23, 12))
                => (0, 1), (0, 2) ... (0, 12), (1, 1), (1, 2)
    '''
    (cycle_begin, cycle_end) = cycle
    (major, minor) = begin
    (end_major, end_minor) = end if end is not None else (None, None)

    while True:
        if end is not None and (major > end_major or (major == end_major and minor > end_minor)):
            return
        yield (major, minor)
        minor += step
        if minor > cycle_end:
            major += 1
            minor = cycle_begin

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
    for (year, month) in _cycle_generator(cycle=(1, 12), begin=earliest_month, end=latest_month):
        mcount = monthly_counts.get((year, month), 0)
        accumulator += mcount
        cumulative_counts.append([datetime.date(year, month, 1), accumulator])

    return cumulative_counts

# analytics views -- all require staff permission

staff_required = user_passes_test(lambda u: u.is_staff)

@staff_required
def new_analytics_index(request,
                        keys_issued_display='chart', keys_issued_interval='yearly',
                        api_calls_display='chart'):
    ignore_internal_keys = request.GET.get('ignore_internal_keys', True)
    ignore_deprecated_apis = request.GET.get('ignore_deprecated_apis', True)
    ignore_inactive_keys = request.GET.get('ignore_inactive_keys', True)

    #TODO: Calls by API
    #TODO: Keys issued
    #TODO: Line chart of keys issued over time
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
    }
    return render(request, 'locksmith/new_analytics_index.html', ctx)


@staff_required
def analytics_index(request):
    c = {}
    c['total_calls'] = 0
    c['total_month_calls'] = 0
    c['total_ytd_calls'] = 0

    now = datetime.datetime.now()
    month_ago = now - datetime.timedelta(30)

    apis = Api.objects.all().annotate(total_calls=Sum('reports__calls'))
    for api in apis:
        api.month_calls = api.reports.filter(date__gte=month_ago).aggregate(calls=Sum('calls'))['calls']
        api.ytd_calls = api.reports.filter(date__year=now.year).aggregate(calls=Sum('calls'))['calls']
        c['total_calls'] += api.total_calls or 0
        c['total_month_calls'] += api.month_calls or 0
        c['total_ytd_calls'] += api.ytd_calls or 0
    c['apis'] = apis

    c['keys_total'] = Key.objects.all().count()
    c['keys_month'] = Key.objects.filter(issued_on__gte=month_ago).count()
    c['keys_ytd'] = Key.objects.filter(issued_on__year=now.year).count()
    c['keys_cumulative'] = _cumulative_by_date(Key, 'issued_on')

    return render_to_response('locksmith/analytics_index.html', c,
                              context_instance=RequestContext(request))

@staff_required
def api_analytics(request, apiname, year=None, month=None):
    api = get_object_or_404(Api, name=apiname)
    endpoint_q = api.reports.values('endpoint').annotate(calls=Sum('calls')).order_by('-calls')
    user_q = api.reports.values('key__email').exclude(key__status='S').annotate(calls=Sum('calls')).order_by('-calls')
    date_q = api.reports.values('date').annotate(calls=Sum('calls')).order_by('date')

    date_constraint = {}
    if year:
        date_constraint['date__year'] = year
        if month:
            date_constraint['date__month'] = month
        endpoint_q = endpoint_q.filter(**date_constraint)
        user_q = user_q.filter(**date_constraint)
        date_q = date_q.filter(**date_constraint)

    dates = api.reports.filter(**date_constraint).dates('date', 'month')
    monthlies = []
    for d in dates:
        item = api.reports.filter(date__year=d.year, date__month=d.month).aggregate(calls=Sum('calls'))
        item['date'] = d
        monthlies.append(item)

    c = {'api': api, 'year': year, 'month': month}
    c['endpoints'], c['endpoint_calls'] = _dictlist_to_lists(endpoint_q, 'endpoint', 'calls')
    #c['users'], c['user_calls'] = _dictlist_to_lists(user_q[:50], 'key__email', 'calls')
    c['user_calls'] = user_q[:50]
    c['monthlies'] = monthlies
    c['timeline'] = date_q

    return render_to_response('locksmith/api_analytics.html', c,
                              context_instance=RequestContext(request))

@staff_required
def key_list(request):

    min_calls = int(request.GET.get('min_calls', 1))

    keys = Key.objects.all().annotate(calls=Sum('reports__calls'),
                                      latest_call=Max('reports__date'))
    keys = keys.filter(calls__gte=min_calls)

    context = {'keys': keys, 'min_calls': min_calls}

    return render_to_response('locksmith/keys_list.html', context,
                              context_instance=RequestContext(request))

@staff_required
def key_analytics(request, key):
    key = get_object_or_404(Key, key=key)
    endpoint_q = key.reports.values('api__name', 'endpoint').annotate(calls=Sum('calls')).order_by('-calls')
    endpoints = [{'endpoint':'.'.join((d['api__name'], d['endpoint'])),
                  'calls': d['calls']} for d in endpoint_q]
    date_q = key.reports.values('date').annotate(calls=Sum('calls')).order_by('date')

    c = {'key': key}
    c['endpoints'], c['endpoint_calls'] = _dictlist_to_lists(endpoints, 'endpoint', 'calls')
    c['timeline'] = date_q

    return render_to_response('locksmith/key_analytics.html', c,
                              context_instance=RequestContext(request))
