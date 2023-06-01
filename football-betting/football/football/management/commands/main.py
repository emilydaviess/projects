# main.py
import requests
from football.models import League, Team, TeamVenue
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

class Command(BaseCommand):
    help = 'Pull raw football data from RapidAPI'
    # https://rapidapi.com/api-sports/api/api-football

    def handle(self, *args, **options):

        self.headers = {
            "X-RapidAPI-Key": "9e42c082bcmshf010546ab6cbf61p10d694jsnd6bffa46a932",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        self.url = "https://api-football-v1.p.rapidapi.com/v3/"

        print("Pulling and Inserting League Data")
        #self.league_data()

        print("Pulling and Inserting Team Data")
        # team data requires us to pass up an optional parameter like league ID
        # for this, we'll pass up the league_id's for the top5 European leagues
        european_leagues = League.objects.filter(
            # Premier League, La Liga , League 1, Serie A, Primeira Liga
            Q(rapid_league_id=39) | Q(name=140) | Q(rapid_league_id=61) | Q(rapid_league_id=135) | Q(rapid_league_id=94)  
        ).values('name','rapid_league_id')
        for league in european_leagues: 
            print("league",league['rapid_league_id'],league['name'])
            self.team_data(league_id=league['rapid_league_id'], season="2022")

    def rapid_api(self, extension, optional_params=False, query_string=False):
        
        url = self.url+extension
        if optional_params: 
            querystring = query_string
            request = requests.get(url, headers=self.headers,params=querystring)
        else: 
            request = requests.get(url, headers=self.headers)

        if not request: 
            print("No data returned from RapidAPI.")
            return

        response = request.json()['response']
        print("response",response)
        if not response: 
            print("No response option within the response.")
            return
        
        return response

    def league_data(self):
        # pull data from rapidAPI with the extension
        response = self.rapid_api('leagues') 
        for row in response:
            print("row",row)
            league = row['league']
            rapid_league_id = league['id']
            name = league['name']
            type = league['name']

            country = row['country']
            country_name = country['name']
            code = country['code'] if country['code'] != None else 'NA'

            # insert data into League table
            League.objects.update_or_create(
                name=name,
                rapid_league_id=rapid_league_id,
                defaults={
                    'country': country_name,
                    'code': code, 
                    'type': type
                }
            )

    def team_data(self,league_id,season):
        # pull data from rapidAPI with the extension
        query_string = {'league':league_id,'season':season}
        response = self.rapid_api('teams',optional_params=True,query_string=query_string) 
        for row in response:
            print("row", row)
            team = row['team']
            rapid_team_id = team['id']
            team_name = team['name']
            code = team['code']
            country = team['country']
            national = team['national']

            venue = row['venue']
            rapid_venue_id = venue['id']
            venue_name = venue['name']
            city = venue['city']
            capacity = venue['capacity']
            surface = venue['surface']

            # insert data into Team table
            team_object, _ = Team.objects.update_or_create(
                name=team_name,
                rapid_team_id=rapid_team_id,
                defaults={
                    'country': country,
                    'national': national,
                    'code': code
                }
            )

            # insert data into TeamVenue
            print("eam_object.id",team_object.id)
            TeamVenue.objects.update_or_create(
                team_id=team_object.id,
                rapid_venue_id=rapid_venue_id,
                defaults={
                    'name': venue_name,
                    'city': city,
                    'capacity': capacity, 
                    'surface': surface
                }
            )