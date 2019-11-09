from django.contrib import admin
from django.contrib.admin import ModelAdmin
from system.models import *
from django.contrib.auth.models import Permission


class MyAdmin(ModelAdmin):
    class Meta:
        exclude = []


class InvitationAdmin(MyAdmin):
    list_display = ["team", "user"]


class TeamInGameAdmin(MyAdmin):
    list_display = ["game", "team"]


class PlayerInGameAdmin(MyAdmin):
    list_display = ["game", "user"]


class GameLevelAdmin(MyAdmin):
    list_display = ["game", "order", "title", "auto_close_time"]


class HintAdmin(MyAdmin):
    list_display = ["level", "available_in", "penalty"]


class BonusAdmin(MyAdmin):
    list_display = ["level", "order", "title", "bonus_time"]


class LevelStatAdmin(MyAdmin):
    list_display = ["level", "team", "started_at", "finished_at"]

admin.site.register(Permission)
admin.site.register(Team)
admin.site.register(UserDetails)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Game)
admin.site.register(GameLevel, GameLevelAdmin)
admin.site.register(Hint, HintAdmin)
admin.site.register(Bonus, BonusAdmin)
admin.site.register(TeamInGame, TeamInGameAdmin)
admin.site.register(PlayerInGame, PlayerInGameAdmin)
admin.site.register(LevelStat, LevelStatAdmin)
