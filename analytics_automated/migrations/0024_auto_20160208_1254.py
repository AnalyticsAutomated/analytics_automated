# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0023_auto_20151110_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task', null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='job',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics_automated.Job'),
        ),
    ]
