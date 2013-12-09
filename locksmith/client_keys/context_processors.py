from locksmith.client_keys.common import get_client_key, get_cached_client_key
from django.conf import settings

def client_key_context(request):
    if hasattr(settings, 'LOCKSMITH_CLIENT_KEY'):
        return {
            'CLIENT_KEY': lambda: get_cached_client_key(settings.LOCKSMITH_CLIENT_KEY, request.get_host(), request.META.get("HTTP_USER_AGENT", ""))
        }
    else:
        return {}