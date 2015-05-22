# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Backend',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('server_type', models.CharField(max_length=64, default=1, choices=[(1, 'GridEngine'), (2, 'RServe')])),
                ('ip', models.CharField(max_length=64, default='127.0.0.1')),
                ('port', models.IntegerField(default=80)),
                ('root_path', models.CharField(max_length=256, default='/tmp/')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('runnable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Parameters',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('flag', models.CharField(max_length=64)),
                ('default', models.CharField(max_length=64)),
                ('bool_valued', models.BooleanField(default=False)),
                ('rest_alias', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('UUID', models.CharField(max_length=64, unique=True)),
                ('input_data', models.BinaryField(null=True)),
                ('status', models.IntegerField()),
                ('email', models.CharField(max_length=256)),
                ('mobile', models.CharField(max_length=256)),
                ('job', models.ForeignKey(to='analytics_automated.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('result_data', models.BinaryField()),
                ('UUID', models.ForeignKey(to='analytics_automated.Queue', to_field='UUID')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('ordering', models.IntegerField(default=0)),
                ('job', models.ForeignKey(to='analytics_automated.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('in_glob', models.CharField(max_length=64)),
                ('out_glob', models.CharField(max_length=64)),
                ('executable', models.CharField(max_length=256)),
                ('backend', models.ForeignKey(to='analytics_automated.Backend')),
            ],
        ),
        migrations.AddField(
            model_name='step',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task'),
        ),
        migrations.AddField(
            model_name='parameters',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task'),
        ),
    ]
