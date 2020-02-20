from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # uses key lookup instead of dict.get
    # to be able to take advantage of the defaultdict
    try:
        return dictionary[key]
    except KeyError:
        return