# Generated by Django 4.2 on 2023-06-17 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0008_alter_playerstats_assists_alter_playerstats_blocks_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerstats',
            name='appearances',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playerstats',
            name='bench',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playerstats',
            name='minutes',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playerstats',
            name='subbed_in',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='playerstats',
            name='subbed_out',
            field=models.IntegerField(null=True),
        ),
    ]
