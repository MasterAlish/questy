# coding=utf-8
import json
import os
import random
from datetime import datetime, timedelta

from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import translation, timezone
from django.utils.translation import ugettext_lazy as _


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name=u"Название", unique=True)
    created_at = models.DateField(auto_now_add=True, verbose_name=u"Дата создания")
    created_by = models.ForeignKey(User, verbose_name=u"Создатель", null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="my_teams")

    def captain(self):
        caps = self.members.filter(is_cap=True)
        if caps.count() > 0:
            return caps.first().user
        return None

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = u"Команды"
        verbose_name = u"Команда"


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=u"Пользователь", related_name="details")
    phone_number = models.CharField(max_length=100, verbose_name=u"Номер телефона", null=True, blank=True)
    current_team = models.ForeignKey(Team, null=True, blank=True, verbose_name=u"Текущая команда",
                                     on_delete=models.SET_NULL, related_name="members")
    is_cap = models.BooleanField(default=False, verbose_name=u"Капитан своей команды")
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


class Game(models.Model):
    author = models.ForeignKey(User, verbose_name=u"Автор игры", related_name="my_games")
    title = models.CharField(max_length=255, verbose_name=u"Название")
    content = RichTextField(verbose_name=u"Описание")
    active = models.BooleanField(verbose_name=u"Игра доступна", default=False)
    min_players = models.IntegerField(verbose_name=u"Минимальное кол-во игроков", default=0, null=True, blank=True)
    max_players = models.IntegerField(verbose_name=u"Максимальное кол-во игроков", default=0, null=True, blank=True)
    starts_at = models.DateTimeField(verbose_name=u"Время начала")
    finishes_at = models.DateTimeField(verbose_name=u"Время конца", null=True, blank=True)
    finished = models.BooleanField(default=False, verbose_name=u"Закончен")
    status = models.CharField(max_length=20, default="not_started", verbose_name=u"Состояние", choices=[
        ["not_started", u"Не начат"], ["started", u"Идет"], ["scoring", u"Подсчет очков"], ["finished", u"Закончен"],
    ])
    sequence = models.CharField(max_length=20, verbose_name=u"Последовательность", default="linear", choices=[
        ["linear", u"Линейная"], ["random", u"Штурмовая"]
    ])

    def ready_to_start(self):
        seconds_to_start = (self.starts_at - timezone.now()).total_seconds()
        return seconds_to_start < 300.0

    def starts_in(self):
        seconds_to_start = (self.starts_at - timezone.now()).total_seconds()
        return int(max(seconds_to_start, 0))

    def has_next_level(self, level):
        return self.levels.filter(order__gt=level.order).exists()

    def get_next_level(self, level):
        return self.levels.filter(order__gt=level.order).first()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = u"Игры"
        verbose_name = u"Игра"
        ordering = ["starts_at"]


class GameLevel(models.Model):
    game = models.ForeignKey(Game, verbose_name=u"Игры", related_name="levels")
    order = models.IntegerField(default=0, verbose_name=u"Уровень")
    title = models.CharField(max_length=255, verbose_name=u"Название уровня")
    content = RichTextField(verbose_name=u"Текст задания")
    right_answers = models.TextField(verbose_name=u"Правильные ответы(json array)")
    auto_close_time = models.IntegerField(verbose_name=u"Время автоперехода(мин)", default=0)

    def is_answer_right(self, answer):
        answers = json.loads(self.right_answers)
        if answer and answer in answers:
            return True
        return False

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = u"Уровни игры"
        verbose_name = u"Уровень игры"
        ordering = ["game", "order"]


class Hint(models.Model):
    level = models.ForeignKey(GameLevel, verbose_name=u"Уровень игры")
    content = RichTextField(verbose_name=u"Текст подсказки")
    available_in = models.IntegerField(verbose_name=u"Доступна через(мин)", default=0)
    penalty = models.IntegerField(verbose_name=u"Штрафное время(мин)", default=0)

    def __unicode__(self):
        return u"Подсказка к уровню '%s'" % self.level.title

    class Meta:
        verbose_name_plural = u"Подсказки"
        verbose_name = u"Подсказка"
        ordering = ["level", "available_in"]


class Bonus(models.Model):
    level = models.ForeignKey(GameLevel, verbose_name=u"Уровень игры")
    order = models.IntegerField(default=0, verbose_name=u"Порядок")
    title = models.CharField(max_length=255, verbose_name=u"Название бонуса")
    content = RichTextField(verbose_name=u"Текст задания бонуса")
    bonus_time = models.IntegerField(verbose_name=u"Бонусное время(мин)", default=0)
    right_answers = models.TextField(verbose_name=u"Правильные ответы(json array)")

    def __unicode__(self):
        return u"Бонус №%d '%s'" % (self.order, self.title)

    class Meta:
        verbose_name_plural = u"Бонусы"
        verbose_name = u"Бонус"
        ordering = ["level", "order"]


class TeamInGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name=u"Игра", related_name="teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name=u"Команда", related_name="games")
    finished = models.BooleanField(default=False, verbose_name=u"Закончили игру")

    class Meta:
        verbose_name_plural = u"Команды в игре"
        verbose_name = u"Команда в игре"


class PlayerInGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name=u"Игра", related_name="players")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, verbose_name=u"В составе команды")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u"Игрок", related_name="games")

    class Meta:
        verbose_name_plural = u"Игроки в игре"
        verbose_name = u"Игрок в игре"


class LevelStat(models.Model):
    level = models.ForeignKey(GameLevel, verbose_name=u"Уровень", related_name="stats", on_delete=models.CASCADE)
    team = models.ForeignKey(Team, verbose_name=u"Команда", on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=u"Время начала уровня")
    finished_at = models.DateTimeField(verbose_name=u"Время конца уровня", null=True, blank=True)
    time_in_level = models.IntegerField(verbose_name=u"Время на уровне(сек)", default=0)
    total_penalty = models.IntegerField(verbose_name=u"Штрафов на уровне(сек)", default=0)
    total_bonus = models.IntegerField(verbose_name=u"Бонусов на уровне(сек)", default=0)

    def __unicode__(self):
        return unicode(self.level)

    class Meta:
        verbose_name_plural = u"Статистика команд на уровнях"
        verbose_name = u"Статистика команды на уровне"
        ordering = ["level__order"]


class Answer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u"Время ответа")
    level_stat = models.ForeignKey(LevelStat, verbose_name=u"Уровень", related_name="answers", on_delete=models.CASCADE)
    answer = models.CharField(max_length=1000, verbose_name=u"Ответ")
    user = models.ForeignKey(User, verbose_name=u"Кто отправил")
    right = models.BooleanField(default=False, verbose_name=u"Правильный")
    bonus_time = models.IntegerField(verbose_name=u"Бонус(сек)", default=0)

    def __unicode__(self):
        return unicode(self.answer)

    class Meta:
        verbose_name_plural = u"Ответы"
        verbose_name = u"Ответ"