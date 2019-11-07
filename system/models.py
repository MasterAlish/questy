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
    name = models.CharField(max_length=100, verbose_name=u"Название", unique=True)
    created_at = models.DateField(auto_now_add=True, verbose_name=u"Дата создания")
    captain = models.ForeignKey(User, verbose_name=u"Капитан", on_delete=models.CASCADE, related_name="teams_i_lead")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u"Команды"
        verbose_name = u"Команда"


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=u"Пользователь", related_name="details")
    phone_number = models.CharField(max_length=100, verbose_name=u"Номер телефона", null=True, blank=True)
    current_team = models.ForeignKey(Team, null=True, blank=True, verbose_name=u"Текущая команда", related_name="members")
    weight = models.IntegerField(null=True, blank=True, verbose_name=u"Вес(кг)")
    height = models.IntegerField(null=True, blank=True, verbose_name=u"Роск(см)")
    sex = models.CharField(default="male", choices=[["male", u"Мужской"], ["female", u"Женский"]], verbose_name=u"Пол",
                           max_length=10)

    def __unicode__(self):
        return unicode(self.user)

    @staticmethod
    def of(user):
        details, _ = UserDetails.objects.get_or_create(user=user)
        return details

    class Meta:
        verbose_name_plural = u"Детали пользователей"
        verbose_name = u"Детали пользователя"


class Invitation(models.Model):
    team = models.ForeignKey(Team, verbose_name=u"В команду", related_name="invitations")
    user = models.ForeignKey(User, verbose_name=u"Кого", related_name="invitations")

    class Meta:
        verbose_name_plural = u"Приглашения в команду"
        verbose_name = u"Приглашение в команду"
