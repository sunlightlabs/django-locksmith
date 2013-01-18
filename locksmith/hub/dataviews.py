import json
import datetime

import dateutil.parser

from django.conf import settings
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from locksmith.hub.models import Api, Key, Report
from unusual.http import BadRequest


@login_required
def calls_by_api(request,
                 begin_date=None, end_date=None,
                 ignore_deprecated=True, ignore_internal_keys=True):
    pass
    
def _resolve_model(model, fields):
    """
    model: Model class
    fields: List of 2-tuples of the form (field, value) in order of descending priority
    """
    for (f, v) in fields:
        if v is not None:
            try:
                kwargs = {f: v}
                obj = model.objects.get(**kwargs)
                return obj
            except model.DoesNotExist:
                pass
            except model.MultipleObjectsReturned:
                pass
    raise model.DoesNotExist()

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

@login_required
def apis_list(request):
    apis = Api.objects.all()
    result = [{'id': api.id, 'name': api.name, 'deprecated': api.push_enabled}
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
        api = _resolve_model(Api, [('id', api_id), ('name', api_name)])
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
def api_calls(request):

    begin_date = parse_date_param(request, 'begin_date')
    end_date = parse_date_param(request, 'end_date')
    ignore_deprecated = parse_bool_param(request, 'ignore_deprecated', False)

    qry = Report.objects
    if ignore_deprecated == True:
        qry = qry.filter(api__push_enabled=False)
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
        qry = qry.filter(status__in='A')
    qry = qry.aggregate(issued=Count('pk'))

    result = {
        'issued': qry['issued']
    }
    if begin_date is not None:
        result['begin_date'] = begin_date.isoformat()
    if end_date is not None:
        result['end_date'] = end_date.isoformat()
    return HttpResponse(content=json.dumps(result), status=200, content_type='application/json')

