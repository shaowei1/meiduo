# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-12-01 13:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weibo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauthsinauser',
            name='access_token',
            field=models.CharField(db_index=True, max_length=256, verbose_name='access_token'),
        ),
    ]
