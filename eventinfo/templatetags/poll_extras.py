from django import template

register = template.Library()


@register.filter(name='is_bookmarked')
def is_bookmarked(value, arg):
    if value.bookmarks.filter(id=arg).exists():
        return True
    else:
        return False
