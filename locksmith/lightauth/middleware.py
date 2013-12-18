from django.conf import settings
from locksmith.lightauth.common import check_key

QS_PARAM = getattr(settings, 'LOCKSMITH_QS_PARAM', 'apikey')
HTTP_HEADER = getattr(settings, 'LOCKSMITH_HTTP_HEADER', 'HTTP_X_APIKEY')

class APIKeyMiddleware(object):
    def process_request(self, request):
        key = request.GET.get(QS_PARAM, None) or request.META.get(HTTP_HEADER, None)
        if key is not None:
            if check_key(key):
                request.apikey = key
