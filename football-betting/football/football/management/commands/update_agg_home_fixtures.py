from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
	name = "Update agg_home_fixtures"

	def handle(self, *args, **options):
		cursor = connection.cursor()
		print("Update MCS UTM report table.")
		cursor.execute("""call sp_update_agg_home_fixtures()""",)
		print(cursor._executed)
		cursor.close()
		