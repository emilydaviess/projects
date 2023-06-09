# Generated by Django 4.2 on 2023-06-17 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0005_agghomefixture_aggawayfixture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('rapid_player_id', models.IntegerField()),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('age', models.IntegerField()),
                ('dob', models.DateField()),
                ('country', models.CharField(max_length=50, null=True)),
                ('nationality', models.CharField(max_length=50, null=True)),
                ('height', models.CharField(max_length=10, null=True)),
                ('weight', models.CharField(max_length=10, null=True)),
                ('injured', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'player',
                'unique_together': {('rapid_player_id',)},
            },
        ),
        migrations.CreateModel(
            name='PlayerStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.CharField(max_length=10, null=True)),
                ('appearances', models.IntegerField()),
                ('minutes', models.IntegerField()),
                ('position', models.CharField(max_length=50, null=True)),
                ('rating', models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True)),
                ('subbed_in', models.IntegerField()),
                ('subbed_out', models.IntegerField()),
                ('bench', models.IntegerField()),
                ('captain', models.BooleanField(default=False)),
                ('shots', models.IntegerField()),
                ('shots_on_target', models.IntegerField()),
                ('goals', models.IntegerField()),
                ('conceded', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('saves', models.IntegerField()),
                ('passes', models.IntegerField()),
                ('key_passes', models.IntegerField()),
                ('accuracy', models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True)),
                ('tackles', models.IntegerField()),
                ('blocks', models.IntegerField()),
                ('interceptions', models.IntegerField()),
                ('duels', models.IntegerField()),
                ('duels_won', models.IntegerField()),
                ('dribbles', models.IntegerField()),
                ('dribble_success', models.IntegerField()),
                ('dribble_past', models.IntegerField()),
                ('fouls_drawn', models.IntegerField()),
                ('fouls_committed', models.IntegerField()),
                ('yellow_cards', models.IntegerField()),
                ('yellow_red_cards', models.IntegerField()),
                ('red_cards', models.IntegerField()),
                ('penalty_won', models.IntegerField()),
                ('penalty_committed', models.IntegerField()),
                ('penalty_scored', models.IntegerField()),
                ('penalty_missed', models.IntegerField()),
                ('penalty_saved', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='football.league')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='football.player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='football.team')),
            ],
            options={
                'db_table': 'player_stats',
                'unique_together': {('player', 'team', 'league', 'season')},
            },
        ),
    ]
