# Generated by Django 4.2 on 2023-06-13 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0002_alter_league_created_alter_team_created_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='league',
            unique_together={('rapid_league_id',)},
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together={('rapid_team_id',)},
        ),
    ]
