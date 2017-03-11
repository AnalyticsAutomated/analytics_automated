# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0012_result_previous_step'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='previous_step',
            field=models.IntegerField(null=True),
        ),
    ]
