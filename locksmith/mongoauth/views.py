from uuid import UUID
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from locksmith.common import get_signature
from locksmith.mongoauth.db import db

def verify_signature(post):
    return get_signature(post, settings.LOCKSMITH_SIGNING_KEY) == post['signature']

@require_POST
@csrf_exempt
def create_key(request):
    if not verify_signature(request.POST):
        return HttpResponseBadRequest('bad signature')
    db.keys.insert({'_id':request.POST['key'],
                    'email':request.POST['email'],
                    'status':request.POST['status']})
    return HttpResponse('OK')

@require_POST
@csrf_exempt
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


@require_POST
@csrf_exempt
def accept_key(request, key_uuid):
    if not verify_signature(request.POST):
        return HttpResponseBadRequest('bad signature')

    if u'status' not in request.POST:
        return HttpResponseBadRequest('no status specified')

    if u'email' not in request.POST:
        return HttpResponseBadRequest('no email specified')

    key_doc = {
        '_id': key_uuid,
        'status': request.POST[u'status'],
        'email': request.POST[u'email']
    }
    db.keys.save(key_doc)
    return HttpResponse('OK')

