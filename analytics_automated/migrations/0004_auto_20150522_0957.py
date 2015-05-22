# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0003_auto_20150522_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='default',
            field=models.CharField(null=True, max_length=64),
        ),
    ]
