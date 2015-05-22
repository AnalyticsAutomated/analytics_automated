# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0002_auto_20150521_1053'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='step',
            unique_together=set([('job', 'ordering')]),
        ),
    ]
