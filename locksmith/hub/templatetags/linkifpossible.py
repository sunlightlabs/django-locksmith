import re
from django import template

register = template.Library()

@register.filter
def linkifpossible(maybe_url):
    if maybe_url is None:
        return ''
    
    maybe_url = maybe_url.strip()
    if len(maybe_url) == 0:
        return ''

    if maybe_url.startswith("http://"):
        return maybe_url

    match = re.match("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$", maybe_url)
    if match is not None:
        # Is just a hostname
        return "http://{}".format(maybe_url)

    return ''
