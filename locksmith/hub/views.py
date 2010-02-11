import datetime
import uuid
from collections import defaultdict
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from locksmith.common import get_signature
from locksmith.hub.models import Api, Key, KeyForm, Report

def verify_signature(post):
    api = get_object_or_404(Api, name=post['api'])
    return get_signature(post, api.signing_key) == post['signature']

@require_POST
def report_calls(request):
    if not verify_signature(request.POST):
        return HttpResponseBadRequest('bad signature')

    api_obj = get_object_or_404(Api, name=request.POST['api'])
    key_obj = get_object_or_404(Key, key=request.POST['key'])

    calls = int(request.POST['calls'])
    try:
        report,c = Report.objects.get_or_create(date=request.POST['date'],
                                                api=api_obj,
                                                key=key_obj,
                                                endpoint=request.POST['endpoint'],
                                                defaults={'calls':calls})
        if not c:
            report.calls = calls
            report.save()
    except Exception, e:
        print e
        raise

    return HttpResponse('OK')

def register(request):
    if request.method == 'POST':
        form = KeyForm(request.POST)
        if form.is_valid():
            newkey = form.save(commit=False)
            newkey.key = uuid.uuid4().hex
            newkey.status = 'U'
            newkey.save()

            email_msg = render_to_string('locksmith/registration_email.txt',
                                         {'key': newkey})
            email_subject = getattr(settings, 'LOCKSMITH_EMAIL_SUBJECT',
                                    'API Registration')
            send_mail(email_subject, email_msg, settings.DEFAULT_FROM_EMAIL,
                      [newkey.email])
            return render_to_response('locksmith/registered.html',
                                      {'key': newkey},
                                      context_instance=RequestContext(request))
    else:
        form = KeyForm()
    return render_to_response('locksmith/register.html', {'form':form},
                              context_instance=RequestContext(request))

def confirm_registration(request, key):
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
    return render_to_response('locksmith/confirmed.html', context,
                              context_instance=RequestContext(request))

# analytics views

def cumulative_by_date(model, datefield):
    by_date = defaultdict(int)
    first_date = None
    for obj in model.objects.all().order_by(datefield):
        if not first_date:
            first_date = getattr(obj, datefield).replace(day=1)
        by_date[getattr(obj, datefield).strftime('%Y-%m')] += 1
    cumulative = [[None, 0]]
    d = first_date
    for i,k in enumerate(sorted(by_date.iterkeys())):
        cumulative.append([d, by_date[k] + cumulative[i][1]])
        d += datetime.timedelta(31)

    return cumulative[1:]

def analytics_index(request):
    apis = Api.objects.all().annotate(total_calls=Sum('reports__calls'))
    month_ago = datetime.datetime.now() - datetime.timedelta(30)
    year_ago = datetime.datetime.now() - datetime.timedelta(365)
    for api in apis:
        api.month_calls = api.reports.filter(date__gte=month_ago).aggregate(calls=Sum('calls'))['calls']
        api.year_calls = api.reports.filter(date__gte=year_ago).aggregate(calls=Sum('calls'))['calls']

    cumulative = cumulative_by_date(Key, 'issued_on')

    return render_to_response('locksmith/analytics_index.html',
                              {'apis':apis, 'cumulative':cumulative,},
                              context_instance=RequestContext(request))

def dictlist_to_lists(dl, *keys):
    ''' convert a list of dictionaries to a dictionary of lists

    >>> dl = [{'a': 'test', 'b': 3}, {'a': 'zaz', 'b': 444},
              {'a': 'wow', 'b': 300}]
    >>> dictlist_to_lists(dl)
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
        item = Report.objects.filter(date__year=d.year, date__month=d.month).aggregate(calls=Sum('calls'))
        item['date'] = d
        monthlies.append(item)

    c = {'api': api, 'year': year, 'month': month}
    c['endpoints'], c['endpoint_calls'] = dictlist_to_lists(endpoint_q, 'endpoint', 'calls')
    c['users'], c['user_calls'] = dictlist_to_lists(user_q[:50], 'key__email', 'calls')
    #c['months'], c['month_calls'] = dictlist_to_lists(monthlies, 'date', 'calls')
    c['monthlies'] = monthlies
    c['timeline'] = date_q

    return render_to_response('locksmith/api_analytics.html', c,
                              context_instance=RequestContext(request))

def keys_analytics(request, apiname):
    keys = Key.objects.all()
    pass

def key_analytics(request, key):
    key = get_object_or_404(Key, key=key)
    endpoint_q = key.reports.values('api__name', 'endpoint').annotate(calls=Sum('calls')).order_by('-calls')
    endpoints = [{'endpoint':'.'.join((d['api__name'], d['endpoint'])),
                  'calls': d['calls']} for d in endpoint_q]
    date_q = key.reports.values('date').annotate(calls=Sum('calls')).order_by('date')

    c = {'key': key}
    c['endpoints'], c['endpoint_calls'] = dictlist_to_lists(endpoints, 'endpoint', 'calls')
    c['timeline'] = date_q

    return render_to_response('locksmith/key_analytics.html', c,
                              context_instance=RequestContext(request))
