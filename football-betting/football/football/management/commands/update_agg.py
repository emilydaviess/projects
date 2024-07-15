from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    name = "Run Aggregation Commands"

    def handle(self, *args, **options):

        # command list to loop through
        command_list = [
            "update_agg_home_fixtures",
            "update_agg_away_fixtures",
            "update_agg_fixtures",
        ]
        for command in command_list:
            print(f'Executing command "{command}"')
            management.call_command(command, *args, **options)
