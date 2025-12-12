import os
from django import template

register = template.Library()

@register.filter
def file_exists(path):
    return os.path.isfile(os.path.join('media', path))
