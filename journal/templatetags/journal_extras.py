# journal/templatetags/journal_extras.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Returns the value for a given key from a dictionary.
    Useful for accessing dictionary values in Django templates,
    especially when the key is dynamic or contains special characters.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None # Return None if not a dictionary or key not found
