import urllib2
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
            print 'sent key {k} to {a}'.format(k=key.key, a=kps.api.name)
        except urllib2.HTTPError as e:
            ctx = {
                'a': str(kps.api.name),
                'k': str(key.key),
                'body': str(e.read())
            }
            print 'Caught HTTPError while pushing key {k} to {a}: {body}'.format(**ctx)
        except Exception as e:
            ctx = {
                'a': str(kps.api.name),
                'k': str(key.key),
                'e': str(e)
            }
            print 'Caught exception while pushing key {k} to {a}: {e}'.format(**ctx)
            print 'retrying'
            push_key.retry()
        kps.status = PUBLISHED
        kps.save()
