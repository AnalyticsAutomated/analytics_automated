# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0004_auto_20150604_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backend',
            name='name',
            field=models.CharField(db_index=True, max_length=64, unique=True),
        ),
    ]
