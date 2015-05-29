# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0002_auto_20150528_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='message',
            field=models.CharField(default='Submitted', blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='result',
            name='name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
