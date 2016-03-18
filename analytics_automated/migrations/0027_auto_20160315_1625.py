# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0026_auto_20160209_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message',
            field=models.CharField(null=True, blank=True, default='Submitted', max_length=2046),
        ),
        migrations.AlterField(
            model_name='submission',
            name='last_message',
            field=models.CharField(null=True, blank=True, default='Submitted', max_length=2046),
        ),
    ]
