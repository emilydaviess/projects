# Generated by Django 4.2 on 2023-06-01 19:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', models.CharField(max_length=10, null=True)),
                ('rapid_team_id', models.IntegerField()),
                ('country', models.CharField(max_length=50, null=True)),
                ('national', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'raw_team',
                'unique_together': {('name', 'rapid_team_id')},
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('type', models.CharField(max_length=150, null=True)),
                ('rapid_league_id', models.IntegerField()),
                ('country', models.CharField(max_length=50, null=True)),
                ('code', models.CharField(max_length=10, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'raw_league',
                'unique_together': {('name', 'rapid_league_id')},
            },
        ),
        migrations.CreateModel(
            name='TeamVenue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rapid_venue_id', models.IntegerField()),
                ('name', models.CharField(max_length=150)),
                ('city', models.CharField(max_length=100, null=True)),
                ('surface', models.CharField(max_length=50, null=True)),
                ('capacity', models.IntegerField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='football.team')),
            ],
            options={
                'db_table': 'raw_team_venue',
                'unique_together': {('team', 'rapid_venue_id')},
            },
        ),
    ]
