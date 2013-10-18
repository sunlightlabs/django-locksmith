import json
import datetime
import calendar
import csv
import dateutil.parser

from django.db.models import Sum, Count, Min, Max, Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from locksmith.hub.models import Api, Key, Report, resolve_model
from locksmith.hub.common import cycle_generator, exclude_internal_keys, exclude_internal_key_reports
from unusual.http import BadRequest

staff_required = user_passes_test(lambda u: u.is_staff)

def _keys_issued_date_range():
    return Key.objects.aggregate(earliest=Min('issued_on'), latest=Max('issued_on'))

def _years():
    extents = _keys_issued_date_range()
    return range(extents['earliest'].year, extents['latest'].year + 1)

def parse_bool(p):
    return unicode(p).lower() in ['y', 't', 'yes', 'true']

def request_param_type_guard(request, param, parse_func, default=None):
    untyped = request.GET.get(param) or request.POST.get(param)
    if untyped is None:
        return default
    try:
        typed = parse_func(untyped)
        return typed
    except (SyntaxError, ValueError):
        raise BadRequest(content='Unparsable {0} value: {1}'.format(param, untyped))

def parse_date_param(request, param, default=None):
    val = request_param_type_guard(request, param, dateutil.parser.parse, default)
    if isinstance(val, datetime.datetime):
        return val.date()
    else:
        return val

def parse_bool_param(request, param, default=None):
    return request_param_type_guard(request, param, parse_bool, default)

def parse_int_param(request, param, default=None):
    return request_param_type_guard(request, param, int, default)

@login_required
def apis_list(request):
    apis = Api.objects.all()
    result = [{'id': api.id, 'name': api.name, 'deprecated': not api.push_enabled}
              for api in apis]
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

def api_calls_monthly(request):
    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    keys_issued_period = _keys_issued_date_range()
    earliest_month = (keys_issued_period['earliest'].year,
                      keys_issued_period['earliest'].month)
    latest_month = (keys_issued_period['latest'].year,
                    keys_issued_period['latest'].month)

    monthly = {}
    for (year, month) in cycle_generator(cycle=(1, 12), begin=earliest_month, end=latest_month):
        monthly[(year, month)] = {'year': year,
                                  'month': month,
                                  'calls': 0}

    qry = Report.objects
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    daily_aggs = qry.values('date').annotate(calls=Sum('calls'))
    for daily in daily_aggs:
        dt = daily['date']
        month = (dt.year, dt.month)
        monthly[month]['calls'] += daily['calls']

    result = {
        'monthly': monthly.values()
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

def api_calls_daily(request):
    today = datetime.date.today()
    a_year_ago = (today - datetime.timedelta(days=365))

    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)
    begin_date = parse_date_param(request, 'begin_date', a_year_ago)
    end_date = parse_date_param(request, 'end_date', today)
    if begin_date > end_date:
        return HttpResponseBadRequest('begin_date must be before end_date')

    cal = calendar.Calendar()
    daily_calls = dict(((dt, {'date': dt.strftime('%Y-%m-%d'), 'calls': 0})
                        for y in range(begin_date.year, end_date.year + 1)
                        for m in range(1, 13)
                        for dt in cal.itermonthdates(y, m)
                        if dt.month == m
                        and dt >= begin_date
                        and dt <= end_date))

    qry = Report.objects.filter(date__range=(begin_date,
                                             end_date))
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    daily_aggs = qry.values('date').annotate(calls=Sum('calls'))
    for daily in daily_aggs:
        dt = daily['date']
        daily_calls[dt]['calls'] = daily['calls']

    result = {
        'daily': daily_calls.values()
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@staff_required
def calls_range(request):
    if request.GET.has_key('begin'):
        begin = request.GET['begin']

        if request.GET.has_key('end'):
            end = request.GET['end']
            end_date = datetime.datetime.strptime(end, '%m/%d/%Y') 
        else:
            end_date = datetime.date()
        #try:
        begin_date = datetime.datetime.strptime(begin,'%m/%d/%Y')

        resp = HttpResponse(status=200, content_type='text/csv')     
        resp['Content-Disposition'] = 'attachment; filename="api_calls_%s_%s"' % (begin, end)

        qry = Report.objects.filter(date__gte=begin_date, date__lte=end_date).extra(select={'day': 'date(date)'}).values('day').annotate(total=Count('date')).order_by('date')
        writer = csv.writer(resp)
        writer.writerow(['Day', 'Total Calls'])
        for day in qry:
            import logging; logging.debug(day)
            writer.writerow([day['day'], day['total']])
        return resp

        #except:
          #  return HttpResponse(content=json.dumps({"error": "Invalid Date Format"}), status=500, content_type='application/json')  


@staff_required
def all_calls(request):
    ignore_deprecated = parse_bool_param(request, 'ignore_deprecated', False)
    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)
    if request.GET.has_key('year'):
        year = int(request.GET['year'])
        qry = Report.objects.filter(date__gte=datetime.date(year, 1, 1),
                                    date__lte=datetime.date(year, 12, 31))
        if ignore_deprecated == True:
            qry = qry.filter(api__push_enabled=True)
        if ignore_internal_keys:
            qry = exclude_internal_key_reports(qry)
        agg = qry.aggregate(calls=Sum('calls'))

        daily_aggs = qry.values('date').annotate(calls=Sum('calls'))
        monthly = dict(((m, {'month': m, 'calls': 0})
                    for m in range(1, 13)))

        for daily in daily_aggs:
            month = daily['date'].month
            monthly[month]['calls'] += daily['calls']

        result = {
            'calls': agg['calls'],
            'monthly': monthly.values(),
            'year': year
        }
        return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')
    else:
        #yearly = Report.objects.raw("select id, extract(YEAR from  reported_time) as year, SUM(calls) as total from locksmith_hub_report group by extract(YEAR from reported_time)")

        qry = Report.objects
        if ignore_deprecated == True:
            qry = qry.filter(api__push_enabled=True)
        if ignore_internal_keys:
            qry = exclude_internal_key_reports(qry)
        daily_aggs = qry.values('date').annotate(calls=Sum('calls'))

        yearly = {}
        for daily in daily_aggs:
            yr = daily['date'].year
            if yr not in yearly:
                yearly[yr] = {'year': yr, 'calls': 0}
            yearly[yr]['calls'] += daily['calls']

        result = {
            'earliest_year': min(yearly.keys()),
            'latest_year': max(yearly.keys()),
            'yearly': yearly.values()
        }
        return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')


@login_required
def calls_to_api(request,
                 api_id=None, api_name=None):

    begin_date = parse_date_param(request, 'begin_date')
    end_date = parse_date_param(request, 'end_date')
    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    qry = Report.objects.filter(api=api) 
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    if begin_date:
        qry = qry.filter(date__gte=begin_date)
    if end_date:
        qry = qry.filter(date__lte=end_date)
    qry = qry.aggregate(calls=Sum('calls'))

    result = {
        'api_id': api.id,
        'api_name': api.name,
        'calls': qry['calls']
    }
    if begin_date is not None:
        result['begin_date'] = begin_date.isoformat()
    if end_date is not None:
        result['end_date'] = end_date.isoformat()
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@login_required
def calls_to_api_yearly(request,
                        api_id=None, api_name=None):
    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    date_extents = _keys_issued_date_range()
    if date_extents['earliest'] and date_extents['latest']:
        earliest_year = date_extents['earliest'].year
        latest_year = date_extents['latest'].year

        qry = Report.objects.filter(api=api)
        if ignore_internal_keys:
            qry = exclude_internal_key_reports(qry)
        agg = qry.aggregate(calls=Sum('calls'))
        daily_aggs = qry.values('date').annotate(calls=Sum('calls'))
        yearly = dict(((y, {'year': y, 'calls': 0})
                       for y in range(earliest_year, latest_year + 1)))
        for daily in daily_aggs:
            yr = daily['date'].year
            yearly[yr]['calls'] += daily['calls']
    else:
        earliest_year = None
        latest_year = None
        agg = { 'calls': 0 }
        yearly = {}

    result = {
        'api_id': api.id,
        'api_name': api.name,
        'earliest_year': earliest_year,
        'latest_year': latest_year,
        'calls': agg['calls'],
        'yearly': yearly.values()
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@login_required
def calls_to_api_monthly(request,
                         api_id=None, api_name=None):
    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)
    year = parse_int_param(request, 'year')
    if year is None:
        return HttpResponseBadRequest("You must specify a year parameter.")

    qry = Report.objects.filter(api=api)
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    qry = qry.filter(date__gte=datetime.date(year, 1, 1),
                     date__lte=datetime.date(year, 12, 31))
    agg = qry.aggregate(calls=Sum('calls'))

    daily_aggs = qry.values('date').annotate(calls=Sum('calls'))
    monthly = dict(((m, {'month': m, 'calls': 0})
                    for m in range(1, 13)))

    for daily in daily_aggs:
        month = daily['date'].month
        monthly[month]['calls'] += daily['calls']

    result = {
        'api_id': api.id,
        'api_name': api.name,
        'calls': agg['calls'],
        'monthly': monthly.values()
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')


@login_required
def calls_to_api_daily(request,
                         api_id=None, api_name=None):
    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)
    end_date = parse_date_param(request, 'end_date')
    begin_date = end_date - datetime.timedelta(days=7)

    qry = Report.objects.filter(api=api)
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    qry = qry.filter(date__gte=begin_date,
                     date__lte=end_date)
    agg = qry.aggregate(calls=Sum('calls'))

    daily_aggs = qry.values('date').annotate(calls=Sum('calls'))

    
    result = {
        'api_id': api.id,
        'api_name': api.name,
        'calls': agg['calls'],
        'daily': []
    }

    for d in daily_aggs:
        result['daily'].append({ 'date': d['date'].strftime('%m-%d-%Y'), 'calls': d['calls']})

    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')


@staff_required
def keys(request):
    """Lists API keys. Compatible with jQuery DataTables."""
    iDisplayStart = parse_int_param(request, 'iDisplayStart')
    iDisplayLength = parse_int_param(request, 'iDisplayLength')
    sEcho = parse_int_param(request, 'sEcho')
    iSortCol_0 = parse_int_param(request, 'iSortCol_0')
    sSortDir_0 = request.GET.get('sSortDir_0', 'asc')
    sSearch = request.GET.get('sSearch')

    columns = ['key', 'email', 'calls', 'latest_call', 'issued_on']
    qry = Key.objects
    if sSearch not in (None, ''):
        qry = qry.filter(Q(key__icontains=sSearch)
                         | Q(email__icontains=sSearch)
                         | Q(name__icontains=sSearch)
                         | Q(org_name__icontains=sSearch)
                         | Q(org_url__icontains=sSearch))
    qry = qry.values('key', 'email', 'issued_on').annotate(calls=Sum('reports__calls'),
                                                           latest_call=Max('reports__date'))
    qry = qry.filter(calls__isnull=False)
    qry = exclude_internal_keys(qry)
    # TODO: Add multi-column sorting
    if iSortCol_0 not in (None, ''):
        sort_col_field = columns[iSortCol_0]
        sort_spec = '{dir}{col}'.format(dir='-' if sSortDir_0 == 'desc' else '',
                                        col=sort_col_field)
        qry = qry.order_by(sort_spec)

    result = {
        'iTotalRecords': Key.objects.count(),
        'iTotalDisplayRecords': qry.count(),
        'sEcho': sEcho,
        'aaData': [[k['key'],
                    '<a href="{0}">{1}</a>'.format(reverse('key_analytics', args=(k['key'], )), k['email']),
                    k['calls'],
                    k['latest_call'].isoformat(),
                    k['issued_on'].date().isoformat()]
                   for k in qry[iDisplayStart:iDisplayStart+iDisplayLength]]
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')


@staff_required
def callers_of_api(request,
                   api_id=None, api_name=None):
    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)
    min_calls = parse_int_param(request, 'min_calls')
    max_calls = parse_int_param(request, 'max_calls')
    top = parse_int_param(request, 'top')

    qry = api.reports
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    qry = (qry.values('key__email', 'key__key')
              .exclude(key__status='S')
              .annotate(calls=Sum('calls')))
    if min_calls is not None:
        qry = qry.filter(calls__gte=min_calls)
    if max_calls is not None:
        qry = qry.filter(calls__lte=max_calls)
    qry = qry.order_by('-calls')
    if top is not None:
        qry = qry[:top]

    result = {
        'callers': [{'key': c['key__key'],
                     'email': c['key__email'],
                     'profile_url': reverse('key_analytics', args=(c['key__key'], )),
                     'calls': c['calls']}
                    for c in qry]
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@login_required
def calls_by_endpoint(request, api_id=None, api_name=None):
    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    qry = Report.objects.filter(api=api)
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    endpoint_aggs = qry.values('endpoint').annotate(calls=Sum('calls'))
    result = {
        'api': {'id': api.id, 'name': api.name},
        'by_endpoint': list(endpoint_aggs)
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@login_required
def calls_from_key_yearly(request, key_uuid):
    try:
        key = Key.objects.get(key=key_uuid)
    except Key.DoesNotExist:
        return HttpResponseNotFound('The requested key was not found.')

    if request.user.email != key.email and request.user.is_staff != True:
        return HttpResponseForbidden()

    date_extents = key.reports.aggregate(earliest=Min('date'), latest=Max('date'))
    if date_extents['earliest'] and date_extents['latest']:
        earliest_year = date_extents['earliest'].year
        latest_year = date_extents['latest'].year

        # Group by date in the database
        qry = key.reports.values('date').annotate(calls=Sum('calls'))
        yearly = dict(((yr, {'year': yr, 'calls': 0})
                       for yr in range(earliest_year, latest_year + 1)))
        # When group by year in python
        for agg in qry:
            yr = agg['date'].year
            yearly[yr]['calls'] += agg['calls']

        result = {
            'key': key_uuid,
            'earliest_year': earliest_year,
            'latest_year': latest_year,
            'yearly': yearly.values()
        }

    else:
        result = {
            'key': key_uuid,
            'earliest_year': None,
            'latest_year': None,
            'yearly': []
        }

    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

def calls_from_key_monthly(request, key_uuid):
    try:
        key = Key.objects.get(key=key_uuid)
    except Key.DoesNotExist:
        return HttpResponseNotFound('The requested key was not found.')

    if request.user.email != key.email and request.user.is_staff != True:
        return HttpResponseForbidden()

    year = parse_int_param(request, 'year')
    if year is None:
        return HttpResponseBadRequest("You must specify a year parameter.")

    qry = key.reports.filter(date__gte=datetime.date(year, 1, 1),
                             date__lte=datetime.date(year, 12, 31))
    qry = qry.values('date').annotate(calls=Sum('calls'))

    monthly = dict(((m, {'month': m, 'calls': 0})
                    for m in range(1, 13)))
    for agg in qry:
        month = agg['date'].month
        monthly[month]['calls'] += agg['calls']

    result = {
        'key': key_uuid,
        'year': year,
        'monthly': monthly.values()
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

def calls_from_key_by_endpoint(request, key_uuid):
    try:
        key = Key.objects.get(key=key_uuid)
    except Key.DoesNotExist:
        return HttpResponseNotFound('The requested key was not found.')

    if request.user.email != key.email and request.user.is_staff != True:
        return HttpResponseForbidden()

    endpoint_aggs = key.reports.values('api__name', 'endpoint').annotate(calls=Sum('calls'))
    result = {
        'key': key_uuid,
        'by_endpoint': [{'api': {'name': agg['api__name']},
                         'endpoint': agg['endpoint'],
                         'calls': agg['calls']}
                        for agg in endpoint_aggs]
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@login_required
def api_calls(request):

    begin_date = parse_date_param(request, 'begin_date')
    end_date = parse_date_param(request, 'end_date')
    ignore_deprecated = parse_bool_param(request, 'ignore_deprecated', False)
    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    qry = Report.objects
    if ignore_deprecated == True:
        qry = qry.filter(api__push_enabled=True)
    if ignore_internal_keys:
        qry = exclude_internal_key_reports(qry)
    if begin_date:
        qry = qry.filter(date__gte=begin_date)
    if end_date:
        qry = qry.filter(date__lte=end_date)
    agg_qry = qry.aggregate(calls=Sum('calls'))
    by_api_qry = qry.values('api__id', 'api__name').annotate(calls=Sum('calls'))

    def obj_for_group(grp):
        return {
            'api_id': grp['api__id'],
            'api_name': grp['api__name'],
            'calls': grp['calls'] or 0
        }

    result = {
        'calls': agg_qry['calls'] or 0,
        'by_api': [obj_for_group(grp)
                   for grp in by_api_qry]
    }
    if begin_date is not None:
        result['begin_date'] = begin_date.isoformat()
    if end_date is not None:
        result['end_date'] = end_date.isoformat()
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@login_required
def keys_issued(request):
    begin_date = parse_date_param(request, 'begin_date')
    end_date = parse_date_param(request, 'end_date')
    ignore_inactive = parse_bool_param(request, 'ignore_inactive', False)
    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    qry = Key.objects
    if ignore_internal_keys:
        qry = exclude_internal_keys(qry)
    if begin_date:
        qry = qry.filter(issued_on__gte=begin_date)
    if end_date:
        qry = qry.filter(issued_on__lte=end_date)
    if ignore_inactive:
        qry = qry.filter(status='A')
    qry = qry.aggregate(issued=Count('pk'))

    result = {
        'issued': qry['issued']
    }
    if begin_date is not None:
        result['begin_date'] = begin_date.isoformat()
    if end_date is not None:
        result['end_date'] = end_date.isoformat()

    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

@login_required
def keys_issued_yearly(request):
    ignore_inactive = parse_bool_param(request, 'ignore_inactive', False)
    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    date_extents = _keys_issued_date_range()
    if date_extents['earliest'] and date_extents['latest']:
        earliest_year = date_extents['earliest'].year
        latest_year = date_extents['latest'].year

        qry = Key.objects
        if ignore_internal_keys:
            qry = exclude_internal_keys(qry)
        if ignore_inactive:
            qry = qry.filter(status='A')

        result = {
            'earliest_year': earliest_year,
            'latest_year': latest_year,
            'yearly': []
        }
        for year in range(earliest_year, latest_year + 1):
            yr_fro = datetime.date(year, 1, 1)
            yr_to = datetime.date(year, 12, 31)
            yr_agg = (qry.filter(issued_on__gte=yr_fro,
                                 issued_on__lte=yr_to)
                         .aggregate(issued=Count('pk')))
            result['yearly'].append({'year': year,
                                     'issued': yr_agg['issued']})
    else:
        result = {
            'earliest_year': None,
            'latest_year': None,
            'yearly': []
        }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')
    
@login_required
def keys_issued_monthly(request):
    year = parse_int_param(request, 'year')
    if year is None:
        return HttpResponseBadRequest("You must specify a year parameter.")
    ignore_inactive = parse_bool_param(request, 'ignore_inactive', False)
    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)

    qry = Key.objects.filter(issued_on__gte=datetime.date(year, 1, 1),
                             issued_on__lte=datetime.date(year, 12, 31))
    if ignore_internal_keys:
        qry = exclude_internal_keys(qry)
    if ignore_inactive:
        qry = qry.filter(status='A')

    daily_aggs = qry.values('issued_on').annotate(issued=Count('pk'))
    monthly = dict(((m, {'month': m, 'issued': 0})
                    for m in range(1, 13)))
    for daily in daily_aggs:
        month = daily['issued_on'].month
        monthly[month]['issued'] += daily['issued']

    agg = qry.aggregate(issued=Count('pk'))

    result = {
        'year': year,
        'issued': agg['issued'],
        'monthly': monthly.values()
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')


def _callers_in_period(begin_date, end_date, api=None, min_calls=100,
                       ignore_internal_keys=True,
                       ignore_autoactivated_keys=True):
    calls_by_key = Report.objects.filter(date__gte=begin_date,
                                         date__lte=end_date)
    if ignore_internal_keys:
        calls_by_key = exclude_internal_key_reports(calls_by_key)
    if api is not None:
        calls_by_key = calls_by_key.filter(api=api)
    calls_by_key = (calls_by_key.values('key__key', 'key__email')
                                .annotate(calls=Sum('calls'))
                                .order_by('-calls'))
    return [{'key': c['key__key'],
             'email': c['key__email'],
             'calls': c['calls']}
            for c in calls_by_key
            if c['calls'] >= min_calls]

def _dates_for_quarter(first_year, first_month):
    if first_month > 10:
        last_year = first_year + 1
        last_month = (first_month + 2) % 12
    else:
        last_year = first_year
        last_month = first_month + 2

    begin_date = datetime.datetime(first_year, first_month, 1)
    days_in_last_month = calendar.monthrange(last_year, last_month)[1]
    end_date = datetime.datetime(last_year, last_month, days_in_last_month)
    return (begin_date, end_date)

def _start_of_previous_quarter(first_year, first_month):
    if first_month < 4:
        return (first_year - 1, (12 - 3 + first_month))
    else:
        return (first_year, first_month - 3)

def _leaderboard_diff(alist, blist):
    for (n, a) in enumerate(alist, start=1):
        a['rank'] = n
    for (n, b) in enumerate(blist, start=1):
        b['rank'] = n

    alookup = dict(((a['key'], a) for a in alist))
    blookup = dict(((b['key'], b) for b in blist))
    akeys = set(alookup.keys())
    bkeys = set(blookup.keys())
    common_keys = akeys & bkeys
    for key in bkeys:
        if key in common_keys:
            blookup[key]['rank_diff'] = blookup[key]['rank'] - alookup[key]['rank']
        else:
            blookup[key]['rank_diff'] = None
    return blookup.values()

@staff_required
def quarterly_leaderboard(request, year, month,
                          api_id=None, api_name=None):
    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        api = None

    ignore_internal_keys = parse_bool_param(request, 'ignore_internal_keys', True)
    ignore_autoactivated_keys = parse_bool_param(request, 'ignore_autoactivated_keys', True)

    year = int(year)
    month = int(month)
    (begin_date, end_date) = _dates_for_quarter(year, month)
    (prev_year, prev_month) = _start_of_previous_quarter(year, month)
    (prev_begin_date, prev_end_date) = _dates_for_quarter(prev_year, prev_month)

    callers = _callers_in_period(begin_date, end_date, api=api)
    prev_callers = _callers_in_period(prev_begin_date, prev_end_date,
                                      api=api,
                                      ignore_internal_keys=ignore_internal_keys,
                                      ignore_autoactivated_keys=ignore_autoactivated_keys)
    leaderboard = _leaderboard_diff(prev_callers, callers)

    result = {
        'earliest_date': begin_date.strftime('%Y-%m-%d'),
        'latest_date': end_date.strftime('%Y-%m-%d'),
        'by_key': leaderboard
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

