import datetime
from django.conf import settings
from locksmith.mongoauth.db import db
from django.http import HttpResponse

QS_PARAM = getattr(settings, 'LOCKSMITH_QS_PARAM', 'apikey')
HTTP_HEADER = getattr(settings, 'LOCKSMITH_HTTP_HEADER', 'HTTP_X_APIKEY')

class APIKeyMiddleware(object):
    def process_request(self, request):
        key = request.GET.get(QS_PARAM, None) or request.META.get(HTTP_HEADER,
                                                                  None)
        if key is not None:
            apikey = db.keys.find_one({'_id':key})
            if apikey:
                request.apikey = apikey
