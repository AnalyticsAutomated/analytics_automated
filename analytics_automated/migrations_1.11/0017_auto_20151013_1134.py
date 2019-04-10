# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0016_auto_20150715_0946'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('step_id', models.IntegerField(null=True)),
                ('message', models.CharField(blank=True, default='Submitted', null=True, max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='message',
            new_name='last_message',
        ),
        migrations.AddField(
            model_name='message',
            name='submission',
            field=models.ForeignKey(to='analytics_automated.Submission', on_delete=models.CASCADE),
        ),
    ]
