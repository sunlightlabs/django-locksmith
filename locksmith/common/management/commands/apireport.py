import datetime
from urlparse import urljoin
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import get_model, Count
from locksmith.common import apicall

APISTATS_APP = 'api'
APISTATS_MODEL = 'LogEntry'
APISTATS_DATE_FIELD = 'timestamp'
APISTATS_ENDPOINT_FIELD = 'method'
APISTATS_USER_FIELD = 'caller_key'

class Command(BaseCommand):
    help = "Push a given day's logs up to the analytics hub"
    args = '[date]'

    requires_model_validation = False

    def handle(self, date=None, *args, **options):
        if date:
            begin = datetime.datetime.strptime(date, '%Y-%m-%d')
        else:
            begin = datetime.datetime.now() - datetime.timedelta(days=1)
            date = begin.strftime('%Y-%m-%d')

        end = begin + datetime.timedelta(days=1)

        timestamp_fieldname = '%s__range' % APISTATS_DATE_FIELD

        Model = get_model(APISTATS_APP, APISTATS_MODEL)
        qs = Model.objects.filter(**{timestamp_fieldname : (begin, end)})
        results = qs.values(APISTATS_ENDPOINT_FIELD, APISTATS_USER_FIELD).annotate(calls=Count('id'))

        endpoint = urljoin(settings.LOCKSMITH_HUB_URL, '/report_views/')

        for item in results:
            data = {'api': settings.LOCKSMITH_API_NAME, 'date':date,
                    'endpoint': item[APISTATS_ENDPOINT_FIELD],
                    'key': item[APISTATS_USER_FIELD], 'calls': item['calls']}
            apicall(endpoint, settings.LOCKSMITH_SIGNING_KEY,
                    api=settings.LOCKSMITH_API_NAME, date=date,
                    endpoint=item[APISTATS_ENDPOINT_FIELD],
                    key=item[APISTATS_USER_FIELD], calls=item['calls'])
