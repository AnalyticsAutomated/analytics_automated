# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0028_auto_20160506_1013'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='step',
            unique_together=set([]),
        ),
    ]
