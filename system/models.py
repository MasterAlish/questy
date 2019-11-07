# coding=utf-8
import os
import random
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name=u"Название")
    created_at = models.DateField(auto_now_add=True, verbose_name=u"Дата создания")
    captain = models.ForeignKey(User, verbose_name=u"Капитан", on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u"Команды"
        verbose_name = u"Команда"


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=u"Пользователь", related_name="details")
    phone_number = models.CharField(max_length=100, verbose_name=u"Номер телефона", null=True, blank=True)
    current_team = models.ForeignKey(Team, null=True, blank=True, verbose_name=u"Текущая команда")
    weight = models.IntegerField(null=True, blank=True, verbose_name=u"Вес(кг)")
    height = models.IntegerField(null=True, blank=True, verbose_name=u"Роск(см)")

    def __unicode__(self):
        return unicode(self.user)

    class Meta:
        verbose_name_plural = u"Детали пользователей"
        verbose_name = u"Детали пользователя"
