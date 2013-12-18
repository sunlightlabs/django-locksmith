from locksmith.common import apicall
import urllib2

try:
    from django.conf import settings
    SIGNING_KEY = settings.LOCKSMITH_SIGNING_KEY
    API_NAME = settings.LOCKSMITH_API_NAME
    ENDPOINT = settings.LOCKSMITH_HUB_URL.replace('analytics', 'accounts') + 'checkkey/'
except:
    SIGNING_KEY = ""
    API_NAME = ""
    ENDPOINT = ""

def check_key(key, signing_key=SIGNING_KEY, api=API_NAME, endpoint=ENDPOINT):
    try:
        apicall(endpoint, signing_key,
            api=api, key=key
        )
        return True
    except urllib2.HTTPError as e:
        if e.code == 404:
            return None
        else:
            raise
