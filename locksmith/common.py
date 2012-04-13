import hashlib
import hmac
import urllib, urllib2

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

