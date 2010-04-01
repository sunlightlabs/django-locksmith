import datetime
from urlparse import urljoin
import urllib2
from django.core.management.base import NoArgsCommand
from django.core.mail import mail_managers
from django.conf import settings
from locksmith.common import apicall
from locksmith.hub.models import KeyPublicationStatus, UNPUBLISHED, PUBLISHED, NEEDS_UPDATE

class Command(NoArgsCommand):
    help = 'push keys that are marked as dirty to the hub'

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 1))
        endpoints = {UNPUBLISHED: 'create_key/', NEEDS_UPDATE: 'update_key/'}
        actions = {UNPUBLISHED: 0, NEEDS_UPDATE: 0}
        failed = 0

        dirty = KeyPublicationStatus.objects.exclude(status=PUBLISHED).select_related()

        for kps in dirty:
            endpoint = urljoin(kps.api.url, endpoints[kps.status])
            try:
                apicall(endpoint, kps.api.signing_key, api=kps.api.name,
                        key=kps.key.key, email=kps.key.email, status=kps.key.status)
                actions[kps.status] += 1
                kps.status = PUBLISHED
                kps.save()
            except urllib2.HTTPError, e:
                failed += 1

        if verbosity == 1:
            if failed and datetime.datetime.now().minute < 2:
                mail_managers('%s failures during pushkeys' % failed, '')
        elif verbosity == 2:
            print 'Published %s new keys, updated %s keys. (%s failures)' % (
                actions[UNPUBLISHED], actions[NEEDS_UPDATE], failed)

