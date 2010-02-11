from django import template

register = template.Library()

@register.filter
def jsdate(date):
    return 'Date.UTC(%s, %s, %s)' % (date.year, date.month-1, date.day)
