from datetime import datetime, time
from hashlib import md5
from django import template
from django.db.models import Sum
from django.utils import timezone

from system.models import Game, Answer, LevelStat

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


@register.inclusion_tag('block/side_menu.html')
def insert_side_menu(user):
    finished_games = Game.objects.filter(finished=True)
    return {'user': user, 'finished_games': finished_games}


@register.inclusion_tag('games/play_menu.html')
def insert_play_menu(my_team, game, current_level=None):
    try:
        stat = LevelStat.objects.get(team=my_team, level=current_level)
        answers = stat.answers.all()
    except:
        answers = []
    return {'game': game, 'my_team': my_team, 'current_level': current_level, 'answers': answers}


@register.inclusion_tag('games/play_levels.html')
def insert_game_levels(game, current_level, team):
    open_levels = LevelStat.objects.filter(level__game=game, team=team).values_list("level__order")
    open_levels = map(lambda l: l[0], open_levels)
    return {'game': game, 'team': team, 'current_level': current_level, 'open_levels': open_levels}


@register.inclusion_tag('block/game.html')
def insert_game(game, request, short=False):
    return {'game': game, 'request': request, 'short': short}


@register.inclusion_tag('block/sex.html')
def sex_icon(sex):
    return {'sex': sex}


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


@register.filter
def gravatar(value):
    return "https://www.gravatar.com/avatar/%s?d=robohash&s=256" % md5(value).hexdigest()


@register.filter
def gravatar_pattern(value):
    return "https://www.gravatar.com/avatar/%s?d=identicon&s=256" % md5(value).hexdigest()


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
