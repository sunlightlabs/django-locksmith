import json
import datetime

import dateutil.parser

from django.conf import settings
from django.db.models import Sum, Count, Min, Max, Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from locksmith.hub.models import Api, Key, Report, resolve_model
from unusual.http import BadRequest

staff_required = user_passes_test(lambda u: u.is_staff)

def _keys_issued_date_range():
    return Key.objects.aggregate(earliest=Min('issued_on'), latest=Max('issued_on'))

def _years():
    extents = _keys_issued_date_range()
    return range(extents['earliest'].year, extents['latest'].year + 1)

@login_required
def calls_by_api(request,
                 begin_date=None, end_date=None,
                 ignore_deprecated=True, ignore_internal_keys=True):
    pass

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
    return request_param_type_guard(request, param, dateutil.parser.parse, default)

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


@login_required
def calls_to_api(request,
                 api_id=None, api_name=None):

    begin_date = parse_date_param(request, 'begin_date')
    end_date = parse_date_param(request, 'end_date')

    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    qry = Report.objects.filter(api=api) 
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

    date_extents = _keys_issued_date_range()
    earliest_year = date_extents['earliest'].year
    latest_year = date_extents['latest'].year

    qry = Report.objects.filter(api=api)
    agg = qry.aggregate(calls=Sum('calls'))
    qry = qry.extra(select={'year': 'extract(year from date)::int'})
    yearly_aggs = qry.values('year').annotate(calls=Sum('calls'))

    yearly = dict([(yr_agg['year'], yr_agg) for yr_agg in yearly_aggs])
    for year in range(earliest_year, latest_year + 1):
        yearly[year] = yearly.get(year,
                                  {'year': year, 'calls': 0})
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
def calls_to_api_monthly(request, year,
                         api_id=None, api_name=None):
    year = int(year)

    if api_id is None and api_name is None:
        return HttpResponseBadRequest('Must specify API id or name.')

    try:
        api = resolve_model(Api, [('id', api_id), ('name', api_name)])
    except Api.DoesNotExist:
        return HttpResponseNotFound('The requested API was not found.')

    qry = Report.objects.filter(api=api)
    qry = qry.filter(date__gte=datetime.date(year, 1, 1),
                     date__lte=datetime.date(year, 12, 31))
    agg = qry.aggregate(calls=Sum('calls'))

    qry = qry.extra(select={'month': 'extract(month from date)::int'})
    monthly_aggs = qry.values('month').annotate(calls=Sum('calls'))

    monthly = dict(((m_agg['month'], m_agg) for m_agg in monthly_aggs))
    for month in range(1, 13):
        monthly[month] = monthly.get(month,
                                     {'month': month, 'calls': 0})
    result = {
        'api_id': api.id,
        'api_name': api.name,
        'calls': agg['calls'],
        'monthly': monthly.values()
    }
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

    columns = ['key', 'email', 'calls', 'latest_call']
    qry = Key.objects
    if sSearch not in (None, ''):
        qry = qry.filter(Q(key__icontains=sSearch) | Q(email__icontains=sSearch))
    qry = qry.values('key', 'email').annotate(calls=Sum('reports__calls'),
                                              latest_call=Max('reports__date'))
    qry = qry.filter(calls__isnull=False)
    # TODO: Add multi-column sorting
    if iSortCol_0 not in (None, ''):
        sort_col_field = columns[iSortCol_0]
        sort_spec = '{dir}{col}'.format(dir='-' if sSortDir_0 == 'desc' else '',
                                        col=sort_col_field)
        qry = qry.order_by(sort_spec)

    result = {
        'iTotalRecord': Key.objects.count(),
        'iTotalDisplayRecords': qry.count(),
        'sEcho': sEcho,
        'aaData': [[k['key'],
                    k['email'],
                    k['calls'],
                    k['latest_call'].isoformat()]
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

    min_calls = parse_int_param(request, 'min_calls')
    max_calls = parse_int_param(request, 'max_calls')
    top = parse_int_param(request, 'top')

    qry = (api.reports
              .values('key__email', 'key__key')
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

    qry = Report.objects.filter(api=api)
    endpoint_aggs = qry.values('endpoint').annotate(calls=Sum('calls'))
    result = {
        'api': {'id': api.id, 'name': api.name},
        'by_endpoint': list(endpoint_aggs)
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')


@login_required
def api_calls(request):

    begin_date = parse_date_param(request, 'begin_date')
    end_date = parse_date_param(request, 'end_date')
    ignore_deprecated = parse_bool_param(request, 'ignore_deprecated', False)

    qry = Report.objects
    if ignore_deprecated == True:
        qry = qry.filter(api__push_enabled=True)
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

    qry = Key.objects
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

    date_extents = _keys_issued_date_range()
    earliest_year = date_extents['earliest'].year
    latest_year = date_extents['latest'].year

    qry = Key.objects
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
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')
    
@login_required
def keys_issued_monthly(request, year):
    year = int(year)
    ignore_inactive = parse_bool_param(request, 'ignore_inactive', False)

    qry = Key.objects.extra(select={'month': 'extract(month from issued_on)::int'})
    qry = qry.filter(issued_on__gte=datetime.date(year, 1, 1),
                     issued_on__lte=datetime.date(year, 12, 31))
    if ignore_inactive:
        qry = qry.filter(status='A')

    monthly_agg = qry.values('month').annotate(issued=Count('pk'))
    monthly = {}
    for agg in monthly_agg:
        monthly[agg['month']] = agg['issued']
    for month in range(1, 13):
        if month not in monthly:
            monthly[month] = 0

    agg = qry.aggregate(issued=Count('pk'))

    result = {
        'year': year,
        'issued': agg['issued'],
        'monthly': [{'month': m, 'issued': cnt} for (m, cnt) in monthly.items()]
    }
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

