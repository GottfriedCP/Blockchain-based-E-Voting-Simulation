import datetime
from django import template

register = template.Library()

@register.filter
def unix_to_date(val):
    return datetime.datetime.fromtimestamp(val)
