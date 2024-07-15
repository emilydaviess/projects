from django.core.management.base import BaseCommand
import seaborn
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
        seaborn.scatterplot(
            x="goals_for",
            y="goals_against",
            hue="team__code",
            palette="hsv",
            data=goals_scored_by_team,
        )

        for line in range(0, goals_scored_by_team.shape[0]):
            plt.text(
                goals_scored_by_team.goals_for[line] + 0.2,
                goals_scored_by_team.goals_against[line],
                goals_scored_by_team.team__code[line],
                horizontalalignment="left",
                size="medium",
                color="black",
                weight="semibold",
            )

        plt.xlabel("Goals For")
        plt.ylabel("Goals Against")
        plt.show()
