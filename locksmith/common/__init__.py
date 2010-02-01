import hashlib
import hmac
import urllib, urllib2
from urlparse import urljoin
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.importlib import import_module
from django.views.decorators.http import require_POST

KEY_STATUSES = (
    ('U', 'Unactivated'),
    ('A', 'Active'),
    ('S', 'Suspended')
)

def get_signature(params, signkey):
    # sorted k,v pairs of everything but signature
    data = sorted([(k,v) for k,v in params.iteritems() if k != 'signature'])
    qs = urllib.urlencode(data)
    return hmac.new(str(signkey), qs, hashlib.sha1).hexdigest()

def apicall(url, signkey, **params):
    params['signature'] = get_signature(params, signkey)
    data = sorted([(k,v) for k,v in params.iteritems()])
    body = urllib.urlencode(data)
    urllib2.urlopen(url, body)

class ViewsBase(object):

    key_model = None

    def __init__(self):
        if not getattr(self, 'key_model', None):
            raise ImproperlyConfigured('%s must define a key_model setting' %
                                       (self.__class__.__name__, setting))

    ## wrapper views

    def create_key_view(self, request):
        if not self.verify_signature(request.POST):
            return HttpResponseBadRequest('bad signature')
        return self.create_key(request)

    def update_key_view(self, request, get_by='key'):
        if not self.verify_signature(request.POST):
            return HttpResponseBadRequest('bad signature')
        return self.update_key(request, get_by)

    ## urls

    @property
    def urls(self):
        return patterns('', *self.get_urls())

    def get_urls(self):
        return [
            url(r'^create_key/$', require_POST(self.create_key_view),
                name='create_key'),
            url(r'^update_key/$', require_POST(self.update_key_view),
                name='update_key'),
            url(r'^update_key_by_email/$', require_POST(self.update_key_view),
                {'get_by':'email'}, name='update_key_by_email'),
        ]

    ## required overrides

    def verify_signature(self, post):
        """ no-op, should be implemented by child classes """
        return False

    def create_key(self, request):
        self.key_model.objects.create(key=request.POST['key'],
                                      email=request.POST['email'],
                                      status=request.POST['status'])
        return HttpResponse('OK')

    def update_key(self, request, get_by='key'):
        # get the key
        if get_by == 'key':
            key = get_object_or_404(self.key_model, key=request.POST['key'])
        elif get_by == 'email':
            key = get_object_or_404(self.key_model, email=request.POST['email'])

        # update key
        key.key = request.POST['key']
        key.email = request.POST['email']
        key.status = request.POST['status']
        key.save()

        return HttpResponse('OK')
