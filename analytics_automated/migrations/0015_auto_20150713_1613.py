# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0014_auto_20150709_1141'),
    ]

    operations = [
        migrations.CreateModel(
            name='Validator',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('validation_type', models.IntegerField(choices=[(0, 'Regular Expression'), (1, 'Image'), (2, 'MP3')], default=0)),
                ('re_string', models.CharField(max_length=512, blank=True, null=True)),
                ('job', models.ForeignKey(to='analytics_automated.Job')),
            ],
        ),
        migrations.AlterField(
            model_name='parameter',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task', related_name='parameters'),
        ),
    ]
