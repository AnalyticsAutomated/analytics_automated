# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0019_auto_20151029_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 11, 3, 12, 49, 31, 515874, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='modified',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 11, 3, 12, 49, 38, 343042, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='backenduser',
            name='priority',
            field=models.IntegerField(default=1, choices=[(0, 'low'), (1, 'medium'), (2, 'high')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='in_glob',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='task',
            name='out_glob',
            field=models.CharField(max_length=256),
        ),
    ]
