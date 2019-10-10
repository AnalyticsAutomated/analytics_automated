# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-03-25 15:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0059_submission_hostname'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('software', models.CharField(blank=True, max_length=256, null=True)),
                ('parameters', models.CharField(blank=True, max_length=256, null=True)),
                ('version', models.CharField(blank=True, max_length=256, null=True)),
                ('dataset', models.CharField(blank=True, max_length=256, null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics_automated.Task')),
            ],
        ),
    ]