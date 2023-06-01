# Generated by Django 4.2 on 2023-06-01 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('type', models.CharField(max_length=50)),
                ('rapid_league_id', models.IntegerField()),
                ('country', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=10)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'raw_league',
            },
        ),
    ]
