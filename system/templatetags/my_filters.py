from datetime import datetime, time

from django import template
from django.db.models import Sum
from django.utils import timezone

register = template.Library()


@register.inclusion_tag('block/navbar.html')
def show_navbar(section, user):
    return {'section': section, 'user': user}


@register.inclusion_tag('block/breadcrumb.html')
def show_breadcrumb(*args):
    arguments = list(args)
    return {'breadcrumbs': arguments}


@register.inclusion_tag('block/messages.html')
def show_messages(messages):
    return {'messages': messages}


@register.filter
def ellipsize(text, n):
    if len(text) > n:
        return text[:n] + ".."
    return text


@register.filter
def multiply(number, number2):
    return number * number2


@register.filter
def subtract(number, number2):
    return number - number2


@register.filter
def divide(number, number2):
    if number2 == 0.0:
        return 0.0
    return number / number2


@register.filter
def nth(iterable, index):
    return iterable[index]


@register.filter
def get(_map, key):
    return _map[key]


@register.filter
def items(map):
    return map.items()


@register.filter
def order_by(queryset, field):
    return queryset.order_by(field)


@register.filter
def if_none(value, default):
    return value if value else default


@register.inclusion_tag("block/pagination.html")
def pages(queryset, request):
    page = int(request.REQUEST.get("page", 1)) - 1
    n = int(request.REQUEST.get("per_page", 20))
    count = queryset.count()
    pages_count = count / n
    if count % n > 0:
        pages_count += 1

    return {'pages': pagination(pages_count, page + 1), 'per_page': n, 'current_page': page + 1, 'last': pages_count}


def pagination(total, page=1, neighbour_count=2):
    result = []
    if page - neighbour_count > 2:
        result.append('first')
    if page - neighbour_count == 2:
        result.append(1)
    for i in range(page - neighbour_count, page + neighbour_count + 1):
        if 0 < i <= total:
            result.append(i)
    if page + neighbour_count < total - 1:
        result.append('last')
    if page + neighbour_count == total - 1:
        result.append(total)
    return result


@register.filter
def paginate(queryset, request):
    page = int(request.REQUEST.get("page", 1)) - 1
    n = int(request.REQUEST.get("per_page", 20))
    return queryset[page * n:page * n + n]


@register.filter
def concat(first, second):
    if not first:
        first = ""
    if not second:
        second = ""
    return first + second
