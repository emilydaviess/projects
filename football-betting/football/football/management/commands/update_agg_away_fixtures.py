from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    name = "Update agg_away_fixtures"

    def handle(self, *args, **options):

        cursor = connection.cursor()
        print("Update sp_update_agg_away_fixtures.")
        cursor.execute(
            """call sp_update_agg_away_fixtures()""",
        )
        print(cursor._executed)
        cursor.close()
