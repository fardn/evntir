from django import template

register = template.Library()


@register.filter(name='is_bookmarked')
def is_bookmarked(value, arg):
    if value.bookmarks.filter(id=arg).exists():
        return True
    else:
        return False


@register.filter(name='item_seats')
def item_seats(value, arg):
    if value[0].items.filter(ticket_id=arg, ordered=False).exists():
        item = value[0].items.filter(ticket_id=arg, ordered=False)
        return item[0].seats
    else:
        return 0
