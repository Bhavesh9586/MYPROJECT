from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Custom template filter to retrieve a value from a dictionary by key
    Usage: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key, 0)
