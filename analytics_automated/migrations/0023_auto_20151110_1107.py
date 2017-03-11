# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0022_auto_20151104_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='stdout_glob',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
