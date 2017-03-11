# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0017_auto_20151013_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='priority',
            field=models.IntegerField(default=1, choices=[(0, 'Low'), (1, 'Normal'), (2, 'High')]),
        ),
        migrations.AlterField(
            model_name='message',
            name='submission',
            field=models.ForeignKey(to='analytics_automated.Submission', related_name='messages'),
        ),
    ]
