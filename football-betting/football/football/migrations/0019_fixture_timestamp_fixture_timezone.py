# Generated by Django 5.0.3 on 2024-06-17 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0018_fixtureplayerstats_conceded_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fixture',
            name='timestamp',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fixture',
            name='timezone',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
