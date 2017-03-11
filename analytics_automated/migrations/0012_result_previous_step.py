# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0011_result_step'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='previous_step',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
    ]
