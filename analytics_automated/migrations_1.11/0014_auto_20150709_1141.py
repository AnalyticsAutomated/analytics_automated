# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0013_auto_20150707_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='submission',
            field=models.ForeignKey(related_name='results', to='analytics_automated.Submission', on_delete=models.CASCADE),
        ),
    ]
