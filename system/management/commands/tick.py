import json
import logging
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from system.features.levels import LevelManager
from system.models import Game, GameLevel, LevelStat

logger = logging.getLogger("django")


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.check_starting_games()
        self.check_finishing_games()

    def check_starting_games(self):
        now = timezone.now()
        games_to_start = Game.objects.filter(active=True, status="not_started", starts_at__lte=now)
        for game in games_to_start:
            print ("Game #%d started\n" % game.id)
            logger.info("Game #%d started" % game.id)
            for participant in game.teams.all():
                team = participant.team
                LevelManager(game, team).init_participation()
        games_to_start.update(status="started")

    def check_finishing_games(self):
        games_in_progress = Game.objects.filter(active=True, status="started")
        for game in games_in_progress:
            if not game.teams.filter(finished=False).exists():
                print ("Game #%d finished\n" % game.id)
                logger.info("Game #%d finished" % game.id)
                game.status = "finished"
                game.finished = True
                game.finishes_at = timezone.now()
                game.save()
