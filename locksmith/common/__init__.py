import hashlib
import hmac
import urllib, urllib2
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.http import require_POST
from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.utils.importlib import import_module

class ApiBase(object):

    # KEY_MODEL

    ## signing internals

    def get_signature(self, params, signkey):
        # sorted k,v pairs of everything but signature
        data = sorted([(k,v) for k,v in params.iteritems() if k != 'signature'])
        qs = urllib.urlencode(data)
        return hmac.new(str(signkey), qs, hashlib.sha1).hexdigest()

    def get_signed_query(self, params, signkey):
        params['signature'] = self.get_signature(params, signkey)
        data = sorted([(k,v) for k,v in params.iteritems()])
        return urllib.urlencode(data)

    def apicall(self, url, signkey, **params):
        body = self.get_signed_query(params, signkey)

        try:
            urllib2.urlopen(url, body)
        except Exception, e:
            print e

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
        self.KEY_MODEL.objects.create(key=request.POST['key'],
                                      email=request.POST['email'],
                                      status=request.POST['status'])
        return HttpResponse('OK')

    def update_key(self, request, get_by='key'):
        # get the key
        if get_by == 'key':
            key = get_object_or_404(self.KEY_MODEL, key=request.POST['key'])
        elif get_by == 'email':
            key = get_object_or_404(self.KEY_MODEL, email=request.POST['email'])

        # update key
        key.key = request.POST['key']
        key.email = request.POST['email']
        key.status = request.POST['status']
        key.save()

        return HttpResponse('OK')

class ApiAuthBase(ApiBase):

    API_NAME = 'set-me'
    SIGNING_KEY = 'set-me'
    API_HUB_URL = 'http://set.me'
    # KEY_MODEL

    def verify_signature(self, post):
        return self.get_signature(post, self.SIGNING_KEY) == post['signature']

    def publish_report(self, date, endpoint, key, calls):
        url = self.API_HUB_URL + '/report_views/'
        self.apicall(url, self.SIGNING_KEY, api=self.API_NAME, date=date,
                     endpoint=endpoint, key=key, calls=calls)

    def publish_new_key(self, key, email, status):
        url = self.API_HUB_URL + '/create_key/'
        self.apicall(url, self.SIGNING_KEY, api=self.API_NAME, key=key,
                     email=email, status=status)

    def publish_key_update(self, key, email, status, get_by='key', ):
        path = {'key':'/update_key/', 'email':'/update_key_by_email/'}[get_by]
        url = self.API_HUB_URL + path
        self.apicall(url, self.SIGNING_KEY, api=self.API_NAME, key=key,
                     email=email, status=status)

_api_instance = None
def get_api_instance():
    global _api_instance
    if _api_instance:
        return _api_class_instance

    path = settings.API_CLASS_PATH

    try:
        dot = path.rindex('.')
        modname, classname = path[:dot], path[dot+1:]
        mod = import_module(modname)
        api_class = getattr(mod, classname)
    except (ValueError, ImportError, AttributeError):
        raise ImproperlyConfigured('Error importing API class from %s' % path)

    _api_instance = api_class()
    return _api_instance
