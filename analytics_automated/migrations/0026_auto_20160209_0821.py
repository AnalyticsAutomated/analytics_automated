# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0025_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='executable',
            field=models.CharField(max_length=2048),
        ),
    ]
