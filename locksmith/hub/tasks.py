import urllib2
from urlparse import urljoin
from locksmith.common import apicall, UNPUBLISHED, PUBLISHED, NEEDS_UPDATE

from celery.task import task

from django.conf import settings

ReplicatedApiNames = getattr(settings, 'LOCKSMITH_REPLICATED_APIS', [])

@task(max_retries=5)
def push_key(key, replicate_too=True):
    if replicate_too:
        for kps in key.pub_statuses.filter(api__push_enabled=True):
            if kps.api.name in ReplicatedApiNames:
                replicate_key.delay(key, kps.api)

    endpoints = {UNPUBLISHED: 'create_key/', NEEDS_UPDATE: 'update_key/'}
    dirty = key.pub_statuses.exclude(status=PUBLISHED).filter(
              api__push_enabled=True).select_related()
    if not dirty:
        print u"Skipping push_key for {k} because all KeyPublicationStatus objects are PUBLISHED.".format(k=key.key)

    # Retrying immediately on failure would allow a broken or unresponsive
    # api to prevent other, properly functioning apis from receiving the key.
    # Thus we use retry_flag to delay the task retry until after attempting
    # to push to all apis.
    retry_flag = False
    for kps in dirty:
        if kps.api.name in ReplicatedApiNames:
            # Skip this API because we've queued a replicate_key task above
            print u"push_key for {k} ignoring {a} because it uses replicate_key.".format(k=key.key, a=kps.api.name)
            continue

        endpoint = urljoin(kps.api.url, endpoints[kps.status])
        try:
            apicall(endpoint, kps.api.signing_key, api=kps.api.name,
                    key=kps.key.key, email=kps.key.email, status=kps.key.status)
            print 'sent key {k} to {a}'.format(k=key.key, a=kps.api.name)
            kps.status = PUBLISHED
            kps.save()

        except Exception as e:
            ctx = {
                'a': str(kps.api.name),
                'k': str(key.key),
                'e': str(e.read()) if isinstance(e, urllib2.HTTPError) else str(e)
            }
            print 'Caught exception while pushing key {k} to {a}: {e}'.format(**ctx)
            print 'Will retry'
            retry_flag = True

    if retry_flag:
        push_key.retry()

@task(max_retries=5)
def replicate_key(key, api):
    kps = key.pub_statuses.get(api=api)
    endpoint = urljoin(kps.api.url, 'replicate_key/{k}/'.format(k=key.key))
    try:
        apicall(endpoint, kps.api.signing_key,
                api=kps.api.name,
                key=kps.key.key,
                email=kps.key.email,
                status=kps.key.status)
        print 'replicated key {k} to {a} with status {s}'.format(k=key.key, s=key.status, a=kps.api.name)
        kps.status = PUBLISHED
        kps.save()

    except Exception as e:
        ctx = {
            'a': str(kps.api.name),
            'k': str(key.key),
            'e': str(e.read()) if isinstance(e, urllib2.HTTPError) else str(e)
        }
        print 'Caught exception while pushing key {k} to {a}: {e}'.format(**ctx)
        print 'Will retry'
        replicate_key.retry()

