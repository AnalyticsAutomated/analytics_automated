# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0030_auto_20160517_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('env', models.CharField(null=True, max_length=129)),
                ('value', models.CharField(null=True, max_length=2048)),
            ],
        ),
        migrations.RemoveField(
            model_name='task',
            name='environment_variables',
        ),
        migrations.AddField(
            model_name='environment',
            name='task',
            field=models.ForeignKey(related_name='environment',
                                    to='analytics_automated.Task',
                                    on_delete=models.CASCADE),
        ),
    ]
