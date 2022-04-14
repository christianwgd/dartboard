from django import template


register = template.Library()


@register.filter
def reverse(value):
    """
    Returns the revese value to 20
    """
    return 21 - value
