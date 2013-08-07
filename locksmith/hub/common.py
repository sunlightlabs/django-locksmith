from django.db.models import Q
from django.conf import settings

def cycle_generator(cycle, step=1, begin=(0, 0), end=None):
    '''
        Generates pairs of values representing a cycle. E.g. clock hours for a day could
        could be generated with:
            _cycle_generator(cycle=(1, 12), step=1, begin=(0, 1), end=(23, 12))
                => (0, 1), (0, 2) ... (0, 12), (1, 1), (1, 2)
    '''
    (cycle_begin, cycle_end) = cycle
    (major, minor) = begin
    (end_major, end_minor) = end if end is not None else (None, None)

    while True:
        if end is not None and (major > end_major or (major == end_major and minor > end_minor)):
            return
        yield (major, minor)
        minor += step
        if minor > cycle_end:
            major += 1
            minor = cycle_begin


def exclude_internal_keys(qry):
    if getattr(settings, 'INTERNAL_ORGANIZATIONS', None):
        qry = qry.exclude(org_name__in=settings.INTERNAL_ORGANIZATIONS)
    if getattr(settings, 'INTERNAL_EMAIL_PATTERN', None):
        qry = qry.exclude(email__endswith=settings.INTERNAL_EMAIL_PATTERN)
    return qry

def exclude_internal_key_reports(qry):
    if getattr(settings, 'INTERNAL_ORGANIZATIONS', None):
        qry = qry.exclude(key__org_name__in=settings.INTERNAL_ORGANIZATIONS)
    if getattr(settings, 'INTERNAL_EMAIL_PATTERN', None):
        qry = qry.exclude(key__email__endswith=settings.INTERNAL_EMAIL_PATTERN)
    return qry

def restrict_to_internal_key_reports(qry):
    internal_orgs = getattr(settings, 'INTERNAL_ORGANIZATIONS', None)
    internal_email_pattern = getattr(settings, 'INTERNAL_EMAIL_PATTERN', None)
    if internal_orgs and internal_email_pattern:
        qry = qry.filter(Q(key__org_name__in=settings.INTERNAL_ORGANIZATIONS)
                       | Q(key__email__endswith=settings.INTERNAL_EMAIL_PATTERN))
    elif internal_orgs:
        qry = qry.filter(key__org_name__in=settings.INTERNAL_ORGANIZATIONS)
    elif internal_email_pattern:
        qry = qry.filter(key__email__endswith=settings.INTERNAL_EMAIL_PATTERN)
    return qry

