# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import analytics_automated.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0015_auto_20150713_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackendUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('login_name', models.CharField(max_length=64, db_index=True, unique=True)),
                ('password', models.CharField(max_length=64, db_index=True, unique=True)),
                ('priority', models.IntegerField(default=2, choices=[(1, 'low'), (2, 'medium'), (3, 'high')])),
                ('backend', models.ForeignKey(related_name='users', to='analytics_automated.Backend', on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='validator',
            name='job',
            field=models.ForeignKey(related_name='validators', to='analytics_automated.Job'),
        ),
        migrations.AlterField(
            model_name='validator',
            name='re_string',
            field=models.CharField(max_length=512, validators=[analytics_automated.models.Validator.validate_re_string], null=True, blank=True),
        ),
    ]
