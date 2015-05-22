# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0004_auto_20150522_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backend',
            name='server_type',
            field=models.IntegerField(choices=[(1, 'GridEngine'), (2, 'RServe')], default=1),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='rest_alias',
            field=models.CharField(unique=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='task',
            name='backend',
            field=models.ForeignKey(null=True, to='analytics_automated.Backend', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
