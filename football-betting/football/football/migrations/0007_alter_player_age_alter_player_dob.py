# Generated by Django 4.2 on 2023-06-17 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0006_player_playerstats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='age',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='dob',
            field=models.DateField(null=True),
        ),
    ]
