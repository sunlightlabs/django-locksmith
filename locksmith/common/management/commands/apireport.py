import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model, Count
from locksmith.common import get_api_instance

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
        api_instance = get_api_instance()

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

        for item in results:
            api_instance.publish_report(date, item[APISTATS_ENDPOINT_FIELD],
                                        item[APISTATS_USER_FIELD],
                                        item['calls'])
