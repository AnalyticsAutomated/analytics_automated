# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0008_auto_20150625_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 6, 26, 9, 50, 47, 382746, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 26, 9, 50, 58, 500691, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='step',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task',
                                    on_delete=models.CASCADE),
        ),
    ]
