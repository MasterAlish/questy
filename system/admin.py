from django.contrib import admin
from django.contrib.admin import ModelAdmin
from system.models import *
from django.contrib.auth.models import Permission


class MyAdmin(ModelAdmin):
    class Meta:
        exclude = []


class InvitationAdmin(MyAdmin):
    list_display = ["team", "user"]

admin.site.register(Permission)
admin.site.register(Team)
admin.site.register(UserDetails)
admin.site.register(Invitation, InvitationAdmin)
