# coding=utf-8
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from system.features.levels import LevelManager
from system.models import TeamInGame, Game, UserDetails, GameLevel, LevelStat, Answer
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
                LevelManager(game, team).init_participation()
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

    def user_has_access_level(self, level, user_details):
        return LevelStat.objects.filter(level=level, team=user_details.current_team).exists()

    def team_finished_the_game(self, team, game):
        finished_levels = LevelStat.objects.filter(level__game=game, team=team, finished_at__isnull=False).count()
        return finished_levels > 0 and finished_levels == game.levels.count()

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
            if self.team_finished_the_game(user_details.current_team, game=game):
                return redirect(reverse("finish_game", kwargs={'game_id': game.id}))
            current_level = self.get_current_level(game, user_details.current_team)

            if self.user_has_access_level(current_level, user_details):
                return redirect(reverse("play_level", kwargs={
                    'game_id': game.id,
                    'level': current_level.order
                }))
            messages.error(request, u"У вас нет доступа к этой игре")
            return redirect(reverse("home"))

        context = {
            'game': game,
            'my_team': user_details.current_team
        }
        return render(request, self.template_name, context)

    def get_current_level(self, game, team):
        not_finished_level_stats = LevelStat.objects.filter(level__game=game, team=team, finished_at__isnull=True)
        if not_finished_level_stats.exists():
            return not_finished_level_stats.first().level
        return game.levels.first()


class PlayGameLevelView(BasePlayView):
    template_name = "games/level.html"

    def check_restriction(self, game, level, user_details):
        if not self.user_can_play(game):
            messages.error(self.request, u"Вы не участвуете в этой игре")
            return False, redirect(reverse("home"))
        if not self.user_has_access_level(level, user_details):
            messages.error(self.request, u"У вас нет доступа на этот уровень")
            return False, redirect(reverse("play_game", kwargs={'game_id': game.id}))
        return True, None

    def dispatch(self, request, *args, **kwargs):
        game = self.get_game(**kwargs)
        level = self.get_level(**kwargs)
        user_details = UserDetails.of(self.request.user)

        ok, response = self.check_restriction(game, level, user_details)
        if not ok:
            return response

        if request.method == "POST":
            answer = request.POST.get("answer", "")
            right_answer = self.dispatch_answer(game, level, answer, user_details)
            if right_answer:
                return redirect(reverse("play_game", kwargs={'game_id': game.id}))
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

    def dispatch_answer(self, game, level, answer, user_details):
        right = level.is_answer_right(answer)
        stat = LevelStat.objects.get(level=level, team=user_details.current_team)
        Answer.objects.create(level_stat=stat, answer=answer, right=right, user=user_details.user)
        if right:
            manager = LevelManager(level.game, user_details.current_team)
            manager.check_level_finished(stat)
            messages.success(self.request, u"Ответ правильный!")
        else:
            messages.error(self.request, u"Ответ неправильный")
        return right


class FinishGameView(BasePlayView):
    template_name = "games/finish.html"

    def dispatch(self, request, *args, **kwargs):
        game = self.get_game(**kwargs)
        user_details = UserDetails.of(self.request.user)

        if not self.user_can_play(game):
            messages.error(request, u"Вы не участвуете в этой игре")
            return redirect(reverse("home"))
        if not self.team_finished_the_game(user_details.current_team, game):
            return redirect(reverse("game_info", kwargs={'game_id': game.id}))

        context = {
            'game': game,
            'my_team': user_details.current_team
        }
        return render(request, self.template_name, context)

    def get_current_level(self, game, team):
        not_finished_level_stats = LevelStat.objects.filter(level__game=game, team=team, finished_at__isnull=True)
        if not_finished_level_stats.exists():
            return not_finished_level_stats.first().level
        return game.levels.first()
