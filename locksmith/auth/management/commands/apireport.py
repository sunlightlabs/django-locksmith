import datetime
from urlparse import urljoin
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import get_model, Count
from locksmith.common import apicall

APP = getattr(settings, 'LOCKSMITH_STATS_APP', 'api')
MODEL = getattr(settings, 'LOCKSMITH_STATS_MODEL', 'LogEntry')
DATE_FIELD = getattr(settings, 'LOCKSMITH_STATS_DATE_FIELD', 'timestamp')
ENDPOINT_FIELD = getattr(settings, 'LOCKSMITH_STATS_ENDPOINT_FIELD', 'method')
USER_FIELD = getattr(settings, 'LOCKSMITH_STATS_USER_FIELD', 'caller_key')

LogModel = get_model(APP, MODEL)

class Command(BaseCommand):
    help = "Push a given day's logs up to the analytics hub"
    args = '[date:YYYY-MM-DD]'
    requires_model_validation = False

    def handle(self, date=None, *args, **options):
        if date:
            # ensure that date entered can be parsed
            entered_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        else:
            # set date to yesterday if not passed in
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            date = yesterday.strftime('%Y-%m-%d')
        print 'pushing logs for %s' % date

        # construct database query
        qs = LogModel.objects.extra(where=["date_trunc('day', {0}) = '{1}'".format(DATE_FIELD, date)]).order_by()
        results = qs.values(ENDPOINT_FIELD, USER_FIELD).annotate(calls=Count('id'))

        endpoint = urljoin(settings.LOCKSMITH_HUB_URL, 'report_calls/')

        # report results
        for item in results:
            apicall(endpoint, settings.LOCKSMITH_SIGNING_KEY,
                    api=settings.LOCKSMITH_API_NAME, date=date,
                    endpoint=item[ENDPOINT_FIELD],
                    key=item[USER_FIELD], calls=item['calls'])
