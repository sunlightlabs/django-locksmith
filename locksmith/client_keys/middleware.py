from django.conf import settings
from locksmith.client_keys.common import check_client_key, check_cached_client_key

import urlparse

QS_PARAM = getattr(settings, 'LOCKSMITH_QS_PARAM', 'apikey')

CLIENT_QS_PARAM = getattr(settings, 'LOCKSMITH_CLIENT_QS_PARAM', 'clientkey')

class ClientKeyMiddleware(object):
    def process_request(self, request):
        key = request.GET.get(CLIENT_QS_PARAM, None)
        hostname = urlparse.urlparse(request.META.get('HTTP_REFERER', "")).netloc
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if key is not None:
            try:
                apikey = check_cached_client_key(key, hostname, user_agent)
                GET = request.GET.copy()
                GET[QS_PARAM] = apikey
                request.GET = GET
            except ValueError as e:
                pass