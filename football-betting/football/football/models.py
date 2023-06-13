from django.db import models

# CREATE YOUR MODELS HERE

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
        unique_together = ['rapid_league_id']

class Season(models.Model):
    season = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "season"
        unique_together = ['season']

class Team(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, null=True)
    rapid_team_id = models.IntegerField()
    country = models.CharField(max_length=50, null=True)
    national = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "team"
        unique_together = ['rapid_team_id']

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
        unique_together = ['team', 'rapid_venue_id'] # a team can share a venue

class Fixture(models.Model):
    rapid_fixture_id = models.IntegerField()
    fixture_date = models.DateTimeField()
    referee = models.CharField(max_length=50)
    venue = models.ForeignKey(TeamVenue, on_delete=models.PROTECT)
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    season = models.CharField(max_length=10, null=True)
    fixture_round = models.CharField(max_length=50, null=True)
    home_team = models.ForeignKey(Team, related_name='home_team',on_delete=models.PROTECT)
    away_team = models.ForeignKey(Team, related_name='away_team',on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fixture"
        unique_together = ['rapid_fixture_id']

class FixtureStats(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.PROTECT)
    home_win = models.BooleanField(default=False, null=True)
    away_win = models.BooleanField(default=False, null=True)
    home_goals = models.IntegerField(null=True)
    away_goals = models.IntegerField(null=True)
    home_ht_score = models.IntegerField(null=True) # home half-time score
    away_ht_score = models.IntegerField(null=True) # away half-time score
    home_ft_score = models.IntegerField(null=True) # home full-time score
    away_ft_score = models.IntegerField(null=True) # away full-time score
    home_et_score = models.IntegerField(null=True, blank=True) # home extra-time score
    away_et_score = models.IntegerField(null=True, blank=True) # away extra-time score
    home_et_penalties = models.IntegerField(null=True, blank=True) # home extra-time penalities 
    away_et_penalties = models.IntegerField(null=True, blank=True) # away extra-time penalities 
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fixture_stats"
        unique_together = ['fixture']

# class Player(models.Model):
#     name = models.CharField(max_length=150)
#     rapid_player_id = models.IntegerField()
#     firstname = models.CharField(max_length=50)
#     lastname = models.CharField(max_length=50)
#     age = models.IntegerField()
#     dob = models.DateField()
#     country = models.CharField(max_length=50, null=True)
#     nationality = models.CharField(max_length=50, null=True)
#     height = models.CharField(max_length=10, null=True)
#     weight = models.CharField(max_length=10, null=True)
#     injured = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "player"
#         unique_together = ['team','rapid_player_id']


# class PlayerMatch(models.Model):
#     player = models.ForeignKey(Player, on_delete=models.PROTECT)
#     team = models.ForeignKey(Team, on_delete=models.PROTECT)
#     league = models.ForeignKey(League, on_delete=models.PROTECT)
#     appearances = models.IntegerField()
#     minutes = models.IntegerField()
#     position = models.CharField(max_length=50, null=True)
#     rating = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
#     subbed_in = models.IntegerField()
#     subbed_out = models.IntegerField()
#     bench = models.IntegerField()
#     captain = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "player_match"
#         unique_together = ['player','team', 'league']

# class PlayerMatchStats(models.Model):
#     player_match = models.ForeignKey(PlayerMatch, on_delete=models.PROTECT)
#     team = models.ForeignKey(Team, on_delete=models.PROTECT)
#     league = models.ForeignKey(League, on_delete=models.PROTECT)
#     appearances = models.IntegerField()
#     minutes = models.IntegerField()
#     position = models.CharField(max_length=50, null=True)
#     rating = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
#     subbed_in = models.IntegerField()
#     subbed_out = models.IntegerField()
#     bench = models.IntegerField()
#     captain = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "player_match_stats"
#         unique_together = ['player_match']




##### AGG
# class AggHomeFixture(models.Model):
#     season = models.CharField(max_length=10)
#     home_team = models.ForeignKey(Team,on_delete=models.PROTECT)
#     team_name = models.CharField(max_length=50)
#     wins = models.IntegerField(null=True)
#     losses = models.IntegerField(null=True)
#     draws = models.IntegerField(null=True)
#     losses = models.IntegerField(null=True)

#     class Meta:
#         db_table = "agg_home_fixture"
#         unique_together = ['season', home_team]