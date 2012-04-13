from urlparse import urljoin
from locksmith.common import apicall, UNPUBLISHED, PUBLISHED, NEEDS_UPDATE

from celery.task import task

@task(max_retries=5)
def push_key(key):
    endpoints = {UNPUBLISHED: 'create_key/', NEEDS_UPDATE: 'update_key/'}
    dirty = key.pub_statuses.exclude(status=PUBLISHED).filter(
              api__push_enabled=True).select_related()
    for kps in dirty:
        endpoint = urljoin(kps.api.url, endpoints[kps.status])
        try:
            apicall(endpoint, kps.api.signing_key, api=kps.api.name,
                    key=kps.key.key, email=kps.key.email, status=kps.key.status)
            print 'sent key to', kps.api.name
        except Exception as e:
            print 'retrying:', e
            push_key.retry()
        kps.status = PUBLISHED
        kps.save()
