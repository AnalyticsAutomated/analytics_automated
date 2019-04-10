# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0027_auto_20160315_1625'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backend',
            name='ip',
        ),
        migrations.RemoveField(
            model_name='backend',
            name='port',
        ),
    ]
