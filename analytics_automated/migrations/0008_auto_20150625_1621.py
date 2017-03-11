# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0007_auto_20150623_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.CharField(max_length=64, unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='step',
            name='task',
            field=models.ForeignKey(related_name='steps', to='analytics_automated.Task'),
        ),
        migrations.AlterField(
            model_name='task',
            name='backend',
            field=models.ForeignKey(related_name='tasks', null=True, to='analytics_automated.Backend', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
