import hashlib
import hmac
from django.utils.six import text_type
from django.utils.six.moves.urllib.request import urlopen
from django.utils.six.moves.urllib.parse import urlencode

def enum(name, **enums):
    E = type(name or 'Enum', (), enums)
    pairs = [(v, n) for (n, v) in enums.items()]
    pairs.sort()
    def __iter__(self):
        return iter(pairs)
    E.__iter__ = __iter__
    return E()

API_OPERATING_STATUSES = (
    (1, 'Normal'),
    (2, 'Degraded Service'),
    (3, 'Service Disruption'),
    (4, 'Undergoing Maintenance')
)

API_STATUSES = enum('ApiStatuses',
                    Stealth=0,
                    Active=1,
                    Deprecated=2,
                    Disabled=3)


KEY_STATUSES = (
    ('U', 'Unactivated'),
    ('A', 'Active'),
    ('S', 'Suspended')
)

UNPUBLISHED, PUBLISHED, NEEDS_UPDATE = range(3)
PUB_STATUSES = (
    (UNPUBLISHED, 'Unpublished'),
    (PUBLISHED, 'Published'),
    (NEEDS_UPDATE, 'Needs Update'),
)

def _bytes(val):
    if isinstance(val, bytes):
        val = text_type(val)
    return val.encode('utf-8')

def get_signature(params, signkey):
    # sorted k,v pairs of everything but signature
    data = sorted([(k, _bytes(v) for k,v in params.items() if k != 'signature'])
    qs = urlencode(data)
    return hmac.new(str(signkey), qs, hashlib.sha1).hexdigest()

def apicall(url, signkey, **params):
    params['signature'] = get_signature(params, signkey)
    data = sorted([(k,v) for k,v in params.items()])
    body = urlencode(data)
    urlopen(url, body)

# taken from http://djangosnippets.org/snippets/564/
from hashlib import sha1
from django.core.cache import cache as _djcache
def cache(seconds = 900):
    def doCache(f):
        def x(*args, **kwargs):
                key = sha1(str(f.__module__) + str(f.__name__) + str(args) + str(kwargs)).hexdigest()
                result = _djcache.get(key)
                if result is None:
                    result = f(*args, **kwargs)
                    _djcache.set(key, result, seconds)
                return result
        return x
    return doCache
