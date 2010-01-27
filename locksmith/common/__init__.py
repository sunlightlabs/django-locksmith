import hashlib
import hmac
import urllib, urllib2
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.http import require_POST
from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.utils.importlib import import_module

KEY_STATUSES = (
    ('U', 'Unactivated'),
    ('A', 'Active'),
    ('S', 'Suspended')
)

class ApiBase(object):

    key_model = None

    _required_settings = ['key_model']

    def __init__(self):
        for setting in self._required_settings:
            if not getattr(self, setting, None):
                raise ImproperlyConfigured('%s must define a %s setting' %
                                           (self.__class__.__name__, setting))

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

class ApiAuthBase(ApiBase):

    key_model = None
    api_name = None
    signing_key = None
    api_hub_url = None
    _required_settings = ('key_model', 'api_name', 'signing_key', 'api_hub_url')

    def verify_signature(self, post):
        return self.get_signature(post, self.signing_key) == post['signature']

    def publish_report(self, date, endpoint, key, calls):
        url = self.api_hub_url + '/report_views/'
        self.apicall(url, self.signing_key, api=self.api_name, date=date,
                     endpoint=endpoint, key=key, calls=calls)

    def publish_new_key(self, key, email, status):
        url = self.api_hub_url + '/create_key/'
        self.apicall(url, self.signing_key, api=self.api_name, key=key,
                     email=email, status=status)

    def publish_key_update(self, key, email, status, get_by='key', ):
        path = {'key':'/update_key/', 'email':'/update_key_by_email/'}[get_by]
        url = self.api_hub_url + path
        self.apicall(url, self.signing_key, api=self.api_name, key=key,
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
