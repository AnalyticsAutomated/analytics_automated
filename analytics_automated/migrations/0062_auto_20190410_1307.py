# Generated by Django 2.2 on 2019-04-10 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics_automated', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuration',
            name='type',
            field=models.IntegerField(blank=True, choices=[(0, 'Software'), (1, 'Dataset'), (2, 'Misc.')], default=0, null=True),
        ),
    ]