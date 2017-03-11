# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='message',
            field=models.CharField(blank=True, max_length=256, null=True, default='Submitted'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.IntegerField(choices=[(0, 'Submitted'), (1, 'Running'), (2, 'Complete'), (3, 'Error'), (4, 'Crash')], default=0),
        ),
    ]
