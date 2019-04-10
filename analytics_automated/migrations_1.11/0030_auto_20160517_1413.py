# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0029_auto_20160506_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='environment_variables',
            field=models.CharField(max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='validator',
            name='validation_type',
            field=models.IntegerField(choices=[(0, 'Regular Expression')], default=0),
        ),
    ]
