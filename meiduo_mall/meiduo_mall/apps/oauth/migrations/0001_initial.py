# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-11-24 12:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthQQUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('openid', models.CharField(db_index=True, max_length=64, verbose_name='openid')),
            ],
            options={
                'verbose_name': 'QQ登录用户数据',
                'verbose_name_plural': 'QQ登录用户数据',
                'db_table': 'tb_oauth_qq',
            },
        ),
    ]
