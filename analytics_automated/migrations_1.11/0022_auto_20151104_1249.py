# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0021_auto_20151104_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='analytics_automated.Task'),
        ),
    ]
