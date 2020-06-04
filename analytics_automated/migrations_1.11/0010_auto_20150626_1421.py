# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0009_auto_20150626_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='step_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='worker_id',
            field=models.CharField(default=None, blank=True, max_length=64, null=True),
        ),
    ]
