from django.utils import timezone

from system.models import LevelStat


class LevelManager(object):
    def __init__(self, game, team):
        self.game = game
        self.team = team

    def init_participation(self):
        if self.game.sequence == "linear":
            self.create_stat_for_first_level()
        elif self.game.sequence == "random":
            self.create_stat_for_all_levels()

    def create_stat_for_first_level(self):
        first_level = self.game.levels.first()
        stat, _ = LevelStat.objects.get_or_create(level=first_level, team=self.team)

    def create_stat_for_all_levels(self):
        for level in self.game.levels.all():
            stat, _ = LevelStat.objects.get_or_create(level=level, team=self.team)

    def check_level_finished(self, level_stat):
        if level_stat.answers.filter(right=True).exists():
            level_stat.finished_at = timezone.now()
            level_stat.time_in_level = (level_stat.finished_at - level_stat.started_at).total_seconds()
            level_stat.save()

            if self.game.has_next_level(level_stat.level):
                next_level = self.game.get_next_level(level_stat.level)
                stat, _ = LevelStat.objects.get_or_create(level=next_level, team=self.team)
            return True
        return False
