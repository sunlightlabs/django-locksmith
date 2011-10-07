from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from locksmith.common import get_signature
from locksmith.auth.models import ApiKey

def verify_signature(post):
    return get_signature(post, settings.LOCKSMITH_SIGNING_KEY) == post['signature']

@csrf_exempt
@require_POST
def create_key(request):
    if not verify_signature(request.POST):
        return HttpResponseBadRequest('bad signature')
    ApiKey.objects.create(key=request.POST['key'],
                          email=request.POST['email'],
                          status=request.POST['status'])
    return HttpResponse('OK')


@csrf_exempt
@require_POST
def update_key(request, get_by='key'):
    if not verify_signature(request.POST):
        return HttpResponseBadRequest('bad signature')
    # get the key
    if get_by == 'key':
        key = get_object_or_404(ApiKey, key=request.POST['key'])
    elif get_by == 'email':
        key = get_object_or_404(ApiKey, email=request.POST['email'])

    # update key
    key.key = request.POST['key']
    key.email = request.POST['email']
    key.status = request.POST['status']
    key.save()

    return HttpResponse('OK')
