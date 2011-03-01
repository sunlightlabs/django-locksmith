from django.conf import settings
from django.http import HttpResponse

class PistonKeyAuthentication(object):

    def is_authenticated(self, request):
        return hasattr(request, 'apikey') and request.apikey['status'] == 'A'

    def challenge(self):
        resp = HttpResponse("Authorization Required", content_type="text/plain")
        resp.status_code = 401
        return resp
