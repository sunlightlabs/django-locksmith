from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
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
            send_mail('Email Subject', email_msg,
                      settings.DEFAULT_FROM_EMAIL, [newkey.email])
            return render_to_response('locksmith/registered.html',
                                      {'key': newkey})
    else:
        form = KeyForm()
    return render_to_response('locksmith/registration.html', {'form':form})

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
    return render_to_response('locksmith/confirmed.html', context)

# analytics views

def analytics_index(request):
    apis = Api.objects.all().annotate(calls=Sum('reports__calls'))
    return render_to_response('locksmith/analytics_index.html',
                              {'apis':apis})
