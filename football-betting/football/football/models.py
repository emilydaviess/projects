from django.db import models


class League(models.Model):
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=150, null=True)
    rapid_league_id = models.IntegerField()
    country = models.CharField(max_length=50, null=True)
    code = models.CharField(max_length=10, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "league"
        unique_together = ["rapid_league_id"]


class Season(models.Model):
    season = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "season"
        unique_together = ["season"]


class Team(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, null=True)
    rapid_team_id = models.IntegerField()
    country = models.CharField(max_length=50, null=True)
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    national = models.BooleanField(default=False)
    image = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "team"
        unique_together = ["rapid_team_id"]


class TeamVenue(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    rapid_venue_id = models.IntegerField()
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, null=True)
    surface = models.CharField(max_length=50, null=True)
    capacity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "team_venue"
        unique_together = ["team", "rapid_venue_id"]  # a team can share a venue


class TeamSeason(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "team_season"
        unique_together = ["team", "league", "season"]


class Fixture(models.Model):
    rapid_fixture_id = models.IntegerField()
    fixture_date = models.DateTimeField()
    timestamp = models.IntegerField()
    timezone = models.CharField(max_length=10, null=True)
    referee = models.CharField(max_length=50, null=True)
    venue = models.ForeignKey(TeamVenue, on_delete=models.PROTECT)
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    fixture_round = models.CharField(max_length=50, null=True)
    home_team = models.ForeignKey(
        Team, related_name="home_team", on_delete=models.PROTECT
    )
    away_team = models.ForeignKey(
        Team, related_name="away_team", on_delete=models.PROTECT
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fixture"
        unique_together = ["rapid_fixture_id"]


class FixtureStats(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.PROTECT)
    home_win = models.BooleanField(default=False, null=True)
    away_win = models.BooleanField(default=False, null=True)
    draw = models.BooleanField(default=False, null=True)
    home_goals = models.IntegerField(null=True)
    away_goals = models.IntegerField(null=True)
    home_ht_score = models.IntegerField(null=True)  # home half-time score
    away_ht_score = models.IntegerField(null=True)  # away half-time score
    home_ft_score = models.IntegerField(null=True)  # home full-time score
    away_ft_score = models.IntegerField(null=True)  # away full-time score
    home_et_score = models.IntegerField(null=True, blank=True)  # home extra-time score
    away_et_score = models.IntegerField(null=True, blank=True)  # away extra-time score
    home_et_penalties = models.IntegerField(
        null=True, blank=True
    )  # home extra-time penalities
    away_et_penalties = models.IntegerField(
        null=True, blank=True
    )  # away extra-time penalities
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fixture_stats"
        unique_together = ["fixture"]


class Player(models.Model):
    name = models.CharField(max_length=150)
    rapid_player_id = models.IntegerField()
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    age = models.IntegerField(null=True)
    dob = models.DateField(null=True)
    country = models.CharField(max_length=50, null=True)
    nationality = models.CharField(max_length=50, null=True)
    height = models.CharField(max_length=10, null=True)
    weight = models.CharField(max_length=10, null=True)
    injured = models.BooleanField(default=False)
    image = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "player"
        unique_together = ["rapid_player_id"]


class FixturePlayerStats(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    minutes = models.IntegerField(null=True)
    number = models.IntegerField(null=True)
    position = models.CharField(max_length=50, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    captain = models.BooleanField(default=False)
    offsides = models.IntegerField(null=True)
    shots = models.IntegerField(null=True)
    shots_on_target = models.IntegerField(null=True)
    goals = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    conceded = models.IntegerField(null=True)
    saves = models.IntegerField(null=True)
    passes = models.IntegerField(null=True)
    key_passes = models.IntegerField(null=True)
    accuracy = models.DecimalField(
        max_digits=10, decimal_places=5, blank=True, null=True
    )
    tackles = models.IntegerField(null=True)
    blocks = models.IntegerField(null=True)
    interceptions = models.IntegerField(null=True)
    duels = models.IntegerField(null=True)
    duels_won = models.IntegerField(null=True)
    dribbles = models.IntegerField(null=True)
    dribble_success = models.IntegerField(null=True)
    dribble_past = models.IntegerField(null=True)
    fouls_drawn = models.IntegerField(null=True)
    fouls_committed = models.IntegerField(null=True)
    yellow_cards = models.IntegerField(null=True)
    yellow_red_cards = models.IntegerField(null=True)
    red_cards = models.IntegerField(null=True)
    penalty_won = models.IntegerField(null=True)
    penalty_committed = models.IntegerField(null=True)
    penalty_scored = models.IntegerField(null=True)
    penalty_missed = models.IntegerField(null=True)
    penalty_saved = models.IntegerField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fixture_player_stats"
        unique_together = ["fixture", "team", "player"]


class PlayerStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    league = models.ForeignKey(
        League, on_delete=models.PROTECT
    )  # the current league the player is playing in
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    appearances = models.IntegerField(null=True)
    minutes = models.IntegerField(null=True)
    position = models.CharField(max_length=50, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    subbed_in = models.IntegerField(null=True)
    subbed_out = models.IntegerField(null=True)
    bench = models.IntegerField(null=True)
    captain = models.BooleanField(default=False)

    # goals
    shots = models.IntegerField(null=True)
    shots_on_target = models.IntegerField(null=True)
    goals = models.IntegerField(null=True)
    conceded = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    saves = models.IntegerField(null=True)
    # passes
    passes = models.IntegerField(null=True)
    key_passes = models.IntegerField(null=True)
    accuracy = models.DecimalField(
        max_digits=10, decimal_places=5, blank=True, null=True
    )
    # tackles
    tackles = models.IntegerField(null=True)
    blocks = models.IntegerField(null=True)
    interceptions = models.IntegerField(null=True)
    # duels
    duels = models.IntegerField(null=True)
    duels_won = models.IntegerField(null=True)
    # dribbles
    dribbles = models.IntegerField(null=True)
    dribble_success = models.IntegerField(null=True)
    dribble_past = models.IntegerField(null=True)
    # fouls
    fouls_drawn = models.IntegerField(null=True)
    fouls_committed = models.IntegerField(null=True)
    # cards
    yellow_cards = models.IntegerField(null=True)
    yellow_red_cards = models.IntegerField(null=True)
    red_cards = models.IntegerField(null=True)
    # penalty
    penalty_won = models.IntegerField(null=True)
    penalty_committed = models.IntegerField(null=True)
    penalty_scored = models.IntegerField(null=True)
    penalty_missed = models.IntegerField(null=True)
    penalty_saved = models.IntegerField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "player_stats"
        unique_together = ["player", "team", "league", "season"]


#### AGG
class AggHomeFixture(models.Model):
    # aggregated home results per season
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT)
    team_name = models.CharField(max_length=50)
    wins = models.IntegerField(null=True)
    losses = models.IntegerField(null=True)
    draws = models.IntegerField(null=True)
    goals_for = models.IntegerField(null=True)  # goals for the home team
    goals_against = models.IntegerField(null=True)  # goals for the away team
    ht_score_for = models.IntegerField(null=True)
    ht_score_against = models.IntegerField(null=True)
    ft_score_for = models.IntegerField(null=True)
    ft_score_against = models.IntegerField(null=True)

    class Meta:
        db_table = "agg_home_fixture"
        unique_together = ["season", "home_team"]


class AggAwayFixture(models.Model):
    # aggregated away results per season
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT)
    team_name = models.CharField(max_length=50)
    wins = models.IntegerField(null=True)
    losses = models.IntegerField(null=True)
    draws = models.IntegerField(null=True)
    goals_for = models.IntegerField(null=True)  # goals for the away team
    goals_against = models.IntegerField(null=True)  # goals for the home team
    ht_score_for = models.IntegerField(null=True)
    ht_score_against = models.IntegerField(null=True)
    ft_score_for = models.IntegerField(null=True)
    ft_score_against = models.IntegerField(null=True)

    class Meta:
        db_table = "agg_away_fixture"
        unique_together = ["season", "away_team"]
