# coding=utf-8
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from system.models import TeamInGame, Game
from system.views import BaseView


class GamesView(BaseView):
    template_name = "games/all_games.html"

    def dispatch(self, request, *args, **kwargs):
        games = Game.objects.filter(finished=False)
        return render(request, self.template_name, {'games': games})


class GameView(BaseView):
    template_name = "games/game_info.html"

    def dispatch(self, request, *args, **kwargs):
        game = Game.objects.get(pk=kwargs["game_id"])
        return render(request, self.template_name, {'game': game})


class TakePartInGameView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            game = Game.objects.get(pk=kwargs["game_id"])
            redirect_to = request.POST.get("next", "/")
            if request.user.teams_i_lead.count() > 0:
                team = request.user.teams_i_lead.first()
                part, created = TeamInGame.objects.get_or_create(game=game, team=team)
                if created:
                    messages.success(request, u"Ваша команда \"%s\" принята к участию в этой игре" % team.name)
                else:
                    messages.info(request, u"Ваша команда уже участвует в этой игре")
            else:
                messages.error(request, u"Вы должны капитаном команды чтобы принять участие")
            return redirect(redirect_to)
        return redirect(reverse("home"))