import datetime
from urlparse import urljoin
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from locksmith.common import apicall

class Command(BaseCommand):
    help = "Push a given day's logs up to the analytics hub"
    args = '[date:YYYY-MM-DD]'
    requires_model_validation = False

    def handle(self, date=None, *args, **options):
        if date:
            # ensure that date entered can be parsed
            dt_begin = datetime.datetime.strptime(date, '%Y-%m-%d')
        else:
            # set date to yesterday if not passed in
            dt_begin = datetime.datetime.now() - datetime.timedelta(days=1)
            date = yesterday.strftime('%Y-%m-%d')
        print 'pushing logs for %s' % date

        dt_end = dt_begin + datetime.timedelta(days=1)

        # construct database query
        qs = LogModel.objects.extra(where=["date_trunc('day', {0}) = '{1}'".format(DATE_FIELD, date)]).order_by()
        results = qs.values(ENDPOINT_FIELD, USER_FIELD).annotate(calls=Count('id'))

        results = db.log.group(['key', 'method'],
                               {"timestamp" {"$gte": dt_begin, "$lt": dt_end},
                               {"count": 0},
                               "function (obj, prev) {prev.count += 1;}")

        endpoint = urljoin(settings.LOCKSMITH_HUB_URL, 'report_calls/')

        # report results
        for item in results:
            apicall(endpoint, settings.LOCKSMITH_SIGNING_KEY,
                    api=settings.LOCKSMITH_API_NAME, date=date,
                    endpoint=item['method'], key=item['key'],
                    calls=item['count'])
