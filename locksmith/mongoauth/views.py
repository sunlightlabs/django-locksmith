from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from locksmith.common import get_signature
from locksmith.mongoauth.db import db

def verify_signature(post):
    return get_signature(post, settings.LOCKSMITH_SIGNING_KEY) == post['signature']

@require_POST
def create_key(request):
    if not verify_signature(request.POST):
        return HttpResponseBadRequest('bad signature')
    db.keys.insert({'_id':request.POST['key'],
                    'email':request.POST['email'],
                    'status':request.POST['status']})
    return HttpResponse('OK')

@require_POST
def update_key(request, get_by='key'):
    if not verify_signature(request.POST):
        return HttpResponseBadRequest('bad signature')
    # get the key
    if get_by == 'key':
        key = db.keys.find_one({'_id':request.POST['key']})
    elif get_by == 'email':
        key = db.keys.find_one({'email':request.POST['email']})

    # update key
    key['_id'] = request.POST['key']
    key['email'] = request.POST['email']
    key['status'] = request.POST['status']
    db.keys.save(key, safe=True)

    return HttpResponse('OK')
