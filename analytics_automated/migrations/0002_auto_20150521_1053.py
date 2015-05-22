# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('flag', models.CharField(max_length=64)),
                ('default', models.CharField(max_length=64)),
                ('bool_valued', models.BooleanField(default=False)),
                ('rest_alias', models.CharField(max_length=64)),
                ('task', models.ForeignKey(to='analytics_automated.Task')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('result_data', models.BinaryField()),
                ('UUID', models.ForeignKey(to_field='UUID', to='analytics_automated.Queue')),
            ],
        ),
        migrations.RemoveField(
            model_name='parameters',
            name='task',
        ),
        migrations.RemoveField(
            model_name='results',
            name='UUID',
        ),
        migrations.DeleteModel(
            name='Parameters',
        ),
        migrations.DeleteModel(
            name='Results',
        ),
    ]
