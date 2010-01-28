from urlparse import urljoin
from django.core.management.base import NoArgsCommand
from django.conf import settings
from locksmith.common import apicall
from locksmith.auth.models import Key, UNPUBLISHED, PUBLISHED, NEEDS_UPDATE

class Command(NoArgsCommand):
    help = 'push keys that are marked as dirty to the hub'

    def handle_noargs(self, **options):
        dirty_keys = Key.objects.exclude(pub_status=PUBLISHED)
        endpoints = {UNPUBLISHED: urljoin(settings.LOCKSMITH_HUB_URL, '/publish_key/'),
                     NEEDS_UPDATE: urljoin(settings.LOCKSMITH_HUB_URL, '/update_key/')}
        for key in dirty_keys:

            apicall(endpoints[key.pub_status], settings.LOCKSMITH_SIGNING_KEY,
                    api=settings.LOCKSMITH_API_NAME, key=key.key,
                    email=key.email, status=key.status)

            key.pub_status = PUBLISHED
            key.save()
