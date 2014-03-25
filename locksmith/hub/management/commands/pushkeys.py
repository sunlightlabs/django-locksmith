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
        failures = []

        # get all non-published keys belonging to APIs with push_enabled
        dirty = KeyPublicationStatus.objects.exclude(status=PUBLISHED).filter(
                                                    api__push_enabled=True).select_related()

        for kps in dirty:
            endpoint = urljoin(kps.api.url, endpoints[kps.status])
            try:
                apicall(endpoint, kps.api.signing_key, api=kps.api.name,
                        key=kps.key.key, email=kps.key.email, status=kps.key.status)
                actions[kps.status] += 1
                kps.status = PUBLISHED
                kps.save()
            except urllib2.HTTPError, e:
                msg = 'endpoint=%s, signing_key=%s, api=%s, key=%s, email=%s, status=%s\n error: %s'
                msg = msg % (endpoint, kps.api.signing_key, kps.api.name,
                             kps.key.key, kps.key.email, kps.key.status, e.read())
                failures.append(msg)


        if verbosity == 1:
            if failures and datetime.datetime.now().minute < 2:
                msg = '--------------\n\n'.join(failures)
                mail_managers('%s failures during pushkeys' % len(failures), msg)
        elif verbosity == 2:
            print 'Published %s new keys, updated %s keys. (%s failures)' % (
                actions[UNPUBLISHED], actions[NEEDS_UPDATE], len(failures))
            for f in failures:
                print f

