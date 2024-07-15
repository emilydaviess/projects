from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    name = "Update agg_fixture"

    def handle(self, *args, **options):

        cursor = connection.cursor()
        print("sp_update_agg_fixtures.")
        cursor.execute(
            """call sp_update_agg_fixtures()""",
        )
        print(cursor._executed)
        cursor.close()
