# Generated by Django 5.0.3 on 2024-03-08 09:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("football", "0009_alter_playerstats_appearances_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="fixturestats",
            name="draw",
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name="team",
            name="league",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="football.league",
            ),
            preserve_default=False,
        ),
    ]