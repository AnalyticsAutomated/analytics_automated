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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('server_type', models.IntegerField(choices=[(1, 'localhost'), (2, 'GridEngine'), (3, 'RServe')], default=1)),
                ('ip', models.GenericIPAddressField(default='127.0.0.1')),
                ('port', models.IntegerField(default=80)),
                ('root_path', models.CharField(default='/tmp/', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('runnable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('flag', models.CharField(max_length=64)),
                ('default', models.CharField(null=True, max_length=64)),
                ('bool_valued', models.BooleanField(default=False)),
                ('rest_alias', models.CharField(unique=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('result_data', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('ordering', models.IntegerField(default=0)),
                ('job', models.ForeignKey(to='analytics_automated.Job', related_name='steps')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('submission_name', models.CharField(null=True, max_length=64)),
                ('UUID', models.CharField(unique=True, null=True, max_length=64)),
                ('email', models.CharField(null=True, max_length=256)),
                ('ip', models.GenericIPAddressField(default='127.0.0.1')),
                ('input_data', models.FileField(upload_to='')),
                ('status', models.IntegerField(choices=[(0, 'Submitted'), (1, 'Running'), (2, 'Complete'), (3, 'Error')], default=0)),
                ('claimed', models.BinaryField()),
                ('worker_id', models.IntegerField(blank=True)),
                ('job', models.ForeignKey(to='analytics_automated.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('in_glob', models.CharField(max_length=64)),
                ('out_glob', models.CharField(max_length=64)),
                ('executable', models.CharField(max_length=256)),
                ('backend', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='analytics_automated.Backend', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='step',
            name='task',
            field=models.ForeignKey(to='analytics_automated.Task'),
        ),
        migrations.AddField(
            model_name='result',
            name='submission',
            field=models.ForeignKey(to='analytics_automated.Submission'),
        ),
        migrations.AddField(
            model_name='result',
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
