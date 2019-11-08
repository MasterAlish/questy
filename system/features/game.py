# coding=utf-8
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from system.models import TeamInGame, Game, UserDetails, GameLevel
from system.views import BaseView


class GamesView(BaseView):
    template_name = "games/all_games.html"

    def dispatch(self, request, *args, **kwargs):
        games = Game.objects.filter(finished=False)
        return render(request, self.template_name, {'games': games})


class GameInfoView(BaseView):
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


class BasePlayView(BaseView):
    def user_can_play(self, game):
        user_details = UserDetails.of(self.request.user)
        return TeamInGame.objects.filter(team=user_details.current_team, game=game).exists()

    def game_is_playable(self, game):
        return not game.finished and game.ready_to_start()

    def get_game(self, **kwargs):
        return Game.objects.get(pk=kwargs["game_id"])

    def get_level(self, **kwargs):
        game = Game.objects.get(pk=kwargs["game_id"])
        return GameLevel.objects.get(game=game, order=kwargs['level'])


class PlayGameView(BasePlayView):
    template_name = "games/play.html"

    def dispatch(self, request, *args, **kwargs):
        game = self.get_game(**kwargs)
        user_details = UserDetails.of(self.request.user)
        if not self.user_can_play(game):
            messages.error(request, u"Вы не участвуете в этой игре")
            return redirect(reverse("home"))
        if not game.finished and game.starts_in() < 1:
            return redirect(reverse("play_level", kwargs={
                'game_id': game.id,
                'level': game.levels.first().order
            }))

        context = {
            'game': game,
            'my_team': user_details.current_team
        }
        return render(request, self.template_name, context)


class PlayGameLevelView(BasePlayView):
    template_name = "games/level.html"

    def dispatch(self, request, *args, **kwargs):
        game = self.get_game(**kwargs)
        level = self.get_level(**kwargs)
        user_details = UserDetails.of(self.request.user)
        if not self.user_can_play(game):
            messages.error(request, u"Вы не участвуете в этой игре")
            return redirect(reverse("home"))

        if request.method == "POST":
            answer = request.POST.get("answer", "")
            right = level.is_answer_right(answer)
            if right:
                messages.success(request, u"Ответ правильный!")
            else:
                messages.error(request, u"Ответ неправильный")
            return redirect(reverse("play_level", kwargs={
                'game_id': game.id,
                'level': level.order
            }))

        context = {
            'game': game,
            'my_team': user_details.current_team,
            'level': level
        }
        return render(request, self.template_name, context)
