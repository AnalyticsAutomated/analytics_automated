# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 15:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0042_remove_job_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='custom_exit_status',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
