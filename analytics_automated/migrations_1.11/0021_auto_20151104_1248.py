# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0020_auto_20151103_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
