import json
import datetime
import uuid
from collections import defaultdict
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, Http404
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from functools import wraps
from locksmith.hub.models import Key, KeyForm, ResendForm, resolve_model
from locksmith.hub.common import cycle_generator

@require_POST
def check_key(request):
    '''
        POST endpoint determining whether or not a key exists and is valid
    '''
    api_objs = list(Api.objects.filter(name=request.POST['api']))
    if not api_objs:
        return HttpResponseBadRequest('Must specify valid API')

    get_object_or_404(Key, key=request.POST['key'], status='A')

    return HttpResponse(json.dumps({'key': request.POST['key'], 'status': 'OK'}), content_type='application/json')


def register(request,
             email_template='locksmith/registration_email.txt',
             registration_template=getattr(settings, 'LOCKSMITH_REGISTER_TEMPLATE', 'locksmith/register.html'),
             registered_template=getattr(settings, 'LOCKSMITH_REGISTERED_TEMPLATE', 'locksmith/registered.html'),
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
            return render_to_response(registered_template, {'key': newkey, 'LOCKSMITH_BASE_TEMPLATE': settings.LOCKSMITH_BASE_TEMPLATE }, context_instance=RequestContext(request))
    else:
        form = KeyForm()
    return render_to_response(registration_template, {'form':form, 'LOCKSMITH_BASE_TEMPLATE': settings.LOCKSMITH_BASE_TEMPLATE}, context_instance=RequestContext(request))

def send_key_email(key, email_template):
    email_msg = render_to_string(email_template, {'key': key, 'LOCKSMITH_BASE_TEMPLATE': settings.LOCKSMITH_BASE_TEMPLATE})
    email_subject = getattr(settings, 'LOCKSMITH_EMAIL_SUBJECT',
                            'API Registration')
    send_mail(email_subject, email_msg, settings.DEFAULT_FROM_EMAIL,
              [key.email])


def resend(request,
           reg_email_template='locksmith/registration_email.txt',
           resend_template=getattr(settings, 'LOCKSMITH_RESEND_TEMPLATE', 'locksmith/resend.html'),
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
                    send_key_email(key, reg_email_template)
                resp['key'] = key
            except Key.DoesNotExist:
                resp['nokey'] = True
        resp['form'] = form
    else:
        resp['form'] = ResendForm()

    resp['LOCKSMITH_BASE_TEMPLATE'] = settings.LOCKSMITH_BASE_TEMPLATE

    return render(request, resend_template, resp)


def confirm_registration(request, key, template="locksmith/confirmed.html"):
    '''
        API key confirmation

        visiting this URL marks a Key as ready for use
    '''
    context = {'LOCKSMITH_BASE_TEMPLATE': settings.LOCKSMITH_BASE_TEMPLATE}
    try:
        context['key'] = key_obj = Key.objects.get(key=key)
        if key_obj.status != 'U':
            context['error'] = 'Key Already Activated'
        else:
            key_obj.status = 'A'
            key_obj.save()
            key_obj.mark_for_update()
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