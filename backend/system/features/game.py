# coding=utf-8
from datetime import timedelta

from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from system.features.levels import LevelManager
from system.models import TeamInGame, Game, UserDetails, GameLevel, LevelStat, Answer
from system.views import BaseView


class BaseGameView(BaseView):
    def user_can_view_game(self, game):
        return game.active or game.author == self.request.user


class GamesView(BaseView):
    template_name = "games/all_games.html"

    def dispatch(self, request, *args, **kwargs):
        my_draft_games = Game.objects.filter(active=False, author=request.user)
        games_in_progress = Game.objects.filter(active=True, status="started")
        games_in_future = Game.objects.filter(active=True, status="not_started")
        six_hours_ago = timezone.now() - timedelta(hours=6)
        just_finished_games = Game.objects.filter(Q(status="finished") | Q(status="scoring")).filter(
            finishes_at__gt=six_hours_ago, active=True)
        return render(request, self.template_name, {
            'my_draft_games': my_draft_games,
            'games_in_progress': games_in_progress,
            'games_in_future': games_in_future,
            'just_finished_games': just_finished_games
        })


class GameInfoView(BaseGameView):
    template_name = "games/game_info.html"

    def dispatch(self, request, *args, **kwargs):
        game = Game.objects.get(pk=kwargs["game_id"])
        if not self.user_can_view_game(game):
            raise Http404()
        return render(request, self.template_name, {'game': game})


class TakePartInGameView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            user_details = UserDetails.of(request.user)
            game = Game.objects.get(pk=kwargs["game_id"])
            if not game.active:
                raise Http404()
            redirect_to = request.POST.get("next", "/")
            if request.user != game.author:
                if user_details.is_cap and user_details.current_team:
                    team = user_details.current_team
                    restricted = self.check_team_restrictions_for_game(team, game)
                    if not restricted:
                        part, created = TeamInGame.objects.get_or_create(game=game, team=team)
                        if created:
                            messages.success(request, u"Ваша команда \"%s\" принята к участию в этой игре" % team.name)
                        else:
                            messages.info(request, u"Ваша команда уже участвует в этой игре")
                else:
                    messages.error(request, u"Вы должны быть капитаном команды чтобы принять участие")
            else:
                messages.error(request, u"Автор игры не может участвовать в игре")
            return redirect(redirect_to)
        return redirect(reverse("home"))

    def check_team_restrictions_for_game(self, team, game):
        if game.min_players and game.min_players > team.members.count():
            messages.error(self.request, u"В команде должно быть минимум %d участника" % game.min_players)
            return True
        if game.max_players and game.max_players < team.members.count():
            messages.error(self.request, u"В команде должно быть максимум %d участника" % game.max_players)
            return True
        return False


class BasePlayView(BaseGameView):
    def user_can_play(self, game):
        user_details = UserDetails.of(self.request.user)
        is_author = game.author == self.request.user
        return is_author or TeamInGame.objects.filter(team=user_details.current_team, game=game).exists()

    def user_has_access_level(self, level, user_details):
        is_author = level.game.author == user_details.user
        return is_author or LevelStat.objects.filter(level=level, team=user_details.current_team).exists()

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

        if not self.user_can_view_game(game):
            return redirect(reverse("home"))
        if not self.user_can_play(game):
            messages.error(request, u"Вы не участвуете в этой игре")
            return redirect(reverse("home"))
        if game.active:
            if game.status == "started":
                if self.team_finished_the_game(user_details.current_team, game=game):
                    if TeamInGame.objects.filter(team=user_details.current_team, game=game, finished=False).exists():
                        TeamInGame.objects.filter(team=user_details.current_team, game=game).update(finished=True)
                    return redirect(reverse("finish_game", kwargs={'game_id': game.id}))
                current_level = self.get_current_level(game, user_details.current_team)

                if self.user_has_access_level(current_level, user_details):
                    return redirect(reverse("play_level", kwargs={
                        'game_id': game.id,
                        'level': current_level.order
                    }))
            elif not game.ready_to_start() and not game.author == request.user:
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
        if not self.user_can_view_game(game):
            return False, redirect(reverse("home"))
        if not self.user_can_play(game):
            messages.error(self.request, u"Вы не участвуете в этой игре")
            return False, redirect(reverse("home"))
        if not self.user_has_access_level(level, user_details):
            messages.error(self.request, u"У вас нет доступа на этот уровень")
            return False, redirect(reverse("play_game", kwargs={'game_id': game.id}))
        if not game.status == "started" and game.author != user_details.user:
            messages.error(self.request, u"Игра не активна")
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
            right = level.is_answer_right(answer)
            if game.active and game.status == "started" and game.author != request.user:
                self.save_answer(game, level, answer, right, user_details)
            if right:
                messages.success(self.request, u"Ответ правильный!")
                return redirect(reverse("play_game", kwargs={'game_id': game.id}))
            else:
                messages.error(self.request, u"Ответ неправильный")
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

    def save_answer(self, game, level, answer, right, user_details):
        stat = LevelStat.objects.get(level=level, team=user_details.current_team)
        Answer.objects.create(level_stat=stat, answer=answer, right=right, user=user_details.user)
        if right:
            manager = LevelManager(level.game, user_details.current_team)
            manager.check_level_finished(stat)


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


class GameStatisticView(BasePlayView):
    template_name = "games/statistics.html"

    def dispatch(self, request, *args, **kwargs):
        game = self.get_game(**kwargs)
        user_details = UserDetails.of(self.request.user)

        if not game.finished and not self.user_can_play(game):
            messages.error(request, u"Статистика еще не доступна")
            return redirect(reverse("game_info", kwargs={'game_id': game.id}))

        level_placement, finish_placement = self.get_stats(game)

        context = {
            'game': game,
            'level_placement': level_placement,
            'finish_placement': finish_placement
        }
        return render(request, self.template_name, context)

    def get_current_level(self, game, team):
        not_finished_level_stats = LevelStat.objects.filter(level__game=game, team=team, finished_at__isnull=True)
        if not_finished_level_stats.exists():
            return not_finished_level_stats.first().level
        return game.levels.first()

    def get_stats(self, game):
        level_placement = {}
        teams_time = {}
        teams_finish_time = {}
        teams_levels_done = {}
        for participant in game.teams.all():
            teams_time[participant.team_id] = 0
            teams_finish_time[participant.team_id] = None
            teams_levels_done[participant.team_id] = 0

        for level in game.levels.all():
            level_stats = level.stats.filter(finished_at__isnull=False)
            teams = []
            for level_stat in level_stats:
                teams_time[level_stat.team_id] += level_stat.time_in_level
                teams.append({
                    'team': level_stat.team,
                    'total_time': teams_time[level_stat.team_id],
                    'finished_at': level_stat.finished_at,
                    'time_in_level': level_stat.time_in_level,
                })
                teams_finish_time[level_stat.team_id] = level_stat.finished_at
                teams_levels_done[level_stat.team_id] += 1
            teams = sorted(teams, key=lambda t: t['total_time'])

            level_placement[level.id] = teams
        finish_placement = []
        for participant in game.teams.all():
            if teams_finish_time[participant.team_id]:
                finish_placement.append({
                    'team': participant.team,
                    'levels_done': teams_levels_done[participant.team_id],
                    'total_time': teams_time[participant.team_id],
                    'finished_at': teams_finish_time[participant.team_id],
                })
        finish_placement = sorted(finish_placement, key=lambda t: t['total_time'])
        finish_placement = sorted(finish_placement, key=lambda t: t['levels_done'], reverse=True)

        return level_placement, finish_placement


class GameStatusView(BasePlayView):

    def dispatch(self, request, *args, **kwargs):
        game = self.get_game(**kwargs)
        user_details = UserDetails.of(self.request.user)
        if not self.user_can_play(game):
            raise Http404()
        return HttpResponse(game.status)
