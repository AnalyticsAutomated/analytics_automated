# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0010_auto_20150626_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='step',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
