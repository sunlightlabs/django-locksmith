import datetime
from urlparse import urljoin
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from locksmith.common import apicall
from locksmith.mongoauth.db import db

class Command(BaseCommand):
    help = "Push a given day's logs up to the analytics hub"
    args = '[date:YYYY-MM-DD]'
    requires_model_validation = False

    def handle(self, date=None, *args, **options):
        if not date:
            # set date to yesterday if not passed in
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            date = yesterday.strftime('%Y-%m-%d')

        print 'pushing logs for %s' % date

        dt_begin = datetime.datetime.strptime(date, '%Y-%m-%d')
        dt_end = dt_begin + datetime.timedelta(days=1)

        # construct database query
        results = db.logs.group(['key', 'method'],
                               {"timestamp": {"$gte": dt_begin, "$lt": dt_end}},
                               {"count": 0},
                               "function (obj, prev) {prev.count += 1;}")

        endpoint = urljoin(settings.LOCKSMITH_HUB_URL, 'report_calls/')

        # report results
        for item in results:
            apicall(endpoint, settings.LOCKSMITH_SIGNING_KEY,
                    api=settings.LOCKSMITH_API_NAME, date=date,
                    endpoint=item['method'], key=item['key'],
                    calls=int(item['count']))
