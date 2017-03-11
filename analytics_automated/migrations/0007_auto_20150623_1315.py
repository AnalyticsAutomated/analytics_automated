# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0006_auto_20150622_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='submission_name',
            field=models.CharField(max_length=64, default='test'),
            preserve_default=False,
        ),
    ]
