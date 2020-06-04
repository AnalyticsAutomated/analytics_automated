# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0005_auto_20150604_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='email',
            field=models.EmailField(max_length=256, null=True),
        ),
    ]
