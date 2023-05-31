from django.db import models

# CREATE YOUR MODELS HERE

class Path(models.Model):
    url = models.CharField(max_length=500, unique=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "raw_path"