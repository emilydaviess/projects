from django.core.management.base import BaseCommand
import plotly.express as px
import matplotlib.pyplot as plt
from football.models import AggFixture
import pandas


class Command(BaseCommand):
    help = "Generates a scatter plot of goals scored by each team"

    def add_arguments(self, parser):
        parser.add_argument("--leagueid", dest="leagueid", type=int)
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        # pull in the data from the database
        if options["leagueid"]:
            goals_scored_by_team = AggFixture.objects.filter(
                team__teamseason__league_id=options["leagueid"]
            ).values(
                "team__code", "wins", "draws", "losses", "goals_for", "goals_against"
            )
        else:
            goals_scored_by_team = AggFixture.objects.values(
                "team__code", "wins", "draws", "losses", "goals_for", "goals_against"
            )
        #  convert the data to a pandas DataFrame
        goals_scored_by_team = pandas.DataFrame(goals_scored_by_team)

        # Assuming df is a pandas DataFrame containing your football data
        fig = px.scatter(
            goals_scored_by_team,
            x="goals_for",
            y="goals_against",
            color="team__code",
            labels={
                "goals_for": "Goals For",
                "goals_against": "Goals Against",
                "team__code": "Team Code",
            },
            title="Goals For vs Goals Against",
            hover_data=["team__code"],  # this will add the team code to the hover text
        )

        fig.show()
