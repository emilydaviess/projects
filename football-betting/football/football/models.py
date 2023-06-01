from django.db import models

# CREATE YOUR MODELS HERE

class League(models.Model):
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=150, null=True)
    rapid_league_id = models.IntegerField()
    country = models.CharField(max_length=50, null=True)
    code = models.CharField(max_length=10, null=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "raw_league"
        unique_together = ['name','rapid_league_id']

class Team(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, null=True)
    rapid_team_id = models.IntegerField()
    country = models.CharField(max_length=50, null=True)
    national = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "raw_team"
        unique_together = ['name','rapid_team_id']

class TeamVenue(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    rapid_venue_id = models.IntegerField()
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, null=True)
    surface = models.CharField(max_length=50, null=True)
    capacity = models.IntegerField()
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "raw_team_venue"
        unique_together = ['team','rapid_venue_id']



