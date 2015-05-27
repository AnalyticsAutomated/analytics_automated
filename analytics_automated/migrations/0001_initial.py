# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Backend',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('server_type', models.IntegerField(choices=[(1, 'localhost'), (2, 'GridEngine'), (3, 'RServe')], default=1)),
                ('ip', models.GenericIPAddressField(default='127.0.0.1')),
                ('port', models.IntegerField(default=80)),
                ('root_path', models.CharField(max_length=256, default='/tmp/')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('runnable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('flag', models.CharField(max_length=64)),
                ('default', models.CharField(null=True, max_length=64)),
                ('bool_valued', models.BooleanField(default=False)),
                ('rest_alias', models.CharField(unique=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('UUID', models.CharField(unique=True, max_length=64)),
                ('input_data', models.BinaryField(null=True)),
                ('status', models.IntegerField()),
                ('email', models.CharField(max_length=256)),
                ('mobile', models.CharField(max_length=256)),
                ('job', models.ForeignKey(to='analytics_automated.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('result_data', models.BinaryField()),
                ('UUID', models.ForeignKey(to_field='UUID', to='analytics_automated.Queue')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ordering', models.IntegerField(default=0)),
                ('job', models.ForeignKey(related_name='steps', to='analytics_automated.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('in_glob', models.CharField(max_length=64)),
                ('out_glob', models.CharField(max_length=64)),
                ('executable', models.CharField(max_length=256)),
                ('backend', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics_automated.Backend')),
            ],
        ),
        migrations.AddField(
            model_name='step',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task'),
        ),
        migrations.AddField(
            model_name='parameter',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task'),
        ),
        migrations.AlterUniqueTogether(
            name='step',
            unique_together=set([('job', 'ordering')]),
        ),
    ]
