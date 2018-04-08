# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('commId', models.CharField(max_length=100)),
                ('authorDispName', models.CharField(max_length=1000)),
                ('text', models.CharField(max_length=10000)),
                ('videoId', models.CharField(max_length=20)),
                ('videoUrl', models.CharField(max_length=1000)),
                ('parentId', models.CharField(max_length=50)),
                ('parentUsername', models.CharField(max_length=1000, blank=True)),
                ('isReply', models.BooleanField()),
                ('updatedAt', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('videoId', models.CharField(max_length=20)),
                ('videoUrl', models.CharField(max_length=1000)),
                ('videoTitle', models.CharField(max_length=300)),
                ('channelId', models.CharField(max_length=30)),
                ('channelUrl', models.CharField(max_length=1000)),
            ],
        ),
    ]
