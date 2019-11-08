# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-11-07 14:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_auto_20191107_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetails',
            name='sex',
            field=models.CharField(choices=[[b'male', '\u041c\u0443\u0436\u0441\u043a\u043e\u0439'], [b'female', '\u0416\u0435\u043d\u0441\u043a\u0438\u0439']], default=b'male', max_length=10, verbose_name='\u041f\u043e\u043b'),
        ),
        migrations.AlterField(
            model_name='team',
            name='captain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams_i_lead', to=settings.AUTH_USER_MODEL, verbose_name='\u041a\u0430\u043f\u0438\u0442\u0430\u043d'),
        ),
    ]