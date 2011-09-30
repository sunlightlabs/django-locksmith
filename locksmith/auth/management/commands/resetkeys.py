import datetime
from urlparse import urljoin
from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings
from locksmith.common import apicall

class Command(NoArgsCommand):
    help = "reset all keys, triggering a request for all keys from the hub"

    def handle_noargs(self, **options):
        print 'resetting all keys for %s' % settings.LOCKSMITH_API_NAME

        endpoint = urljoin(settings.LOCKSMITH_HUB_URL, 'reset_keys/')

        apicall(endpoint, settings.LOCKSMITH_SIGNING_KEY,
                api=settings.LOCKSMITH_API_NAME)
