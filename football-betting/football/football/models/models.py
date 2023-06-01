from django.db import models

# CREATE YOUR MODELS HERE

class League(models.Model):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50)
    rapid_league_id = models.IntegerField()
    country = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "raw_league"