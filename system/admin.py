from django.contrib import admin
from django.contrib.admin import ModelAdmin
from system.models import *
from django.contrib.auth.models import Permission


class MyAdmin(ModelAdmin):
    class Meta:
        exclude = []

admin.site.register(Permission)
