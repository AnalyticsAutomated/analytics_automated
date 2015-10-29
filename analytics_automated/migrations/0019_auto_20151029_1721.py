# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0018_auto_20151029_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='priority',
            field=models.IntegerField(default=1, choices=[(0, 'Low'), (1, 'Medium'), (2, 'High')]),
        ),
    ]
