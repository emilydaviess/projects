# main.py
import requests
from football.models import League, Team, TeamVenue, Season, Fixture, FixtureStats, Player,PlayerStats
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.conf import settings

class Command(BaseCommand):
    help = 'Pull raw football data from RapidAPI'
    # https://rapidapi.com/api-sports/api/api-football
    # https://rapidapi.com/Wolf1984/api/football-xg-statistics (XG)

    def add_arguments(self, parser):
        parser.add_argument("--override", dest="override", action="store_true")
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):

        self.headers = {
            "X-RapidAPI-Host": "9e42c082bcmshf010546ab6cbf61p10d694jsnd6bffa46a932",
            "X-RapidAPI-Key": settings.X_RAPIDAPI_KEY_PASSWORD
        }
        self.season = "2022"
        self.url = "https://api-football-v1.p.rapidapi.com/v3/"


        # 1. Pull and Insert League Data i.e. Premier League, La Liga
        # check if we already have data in League, only run if League is empty
        if League.objects.count() == 0 or options['override']:
            print("Pulling and Inserting League Data")
            self.league_data()

        # 2. Pull and Insert Seasons i.e. 2022

        # check if we already have data in Season, only run if League is empty
        if Season.objects.count() == 0 or options['override']:
            print("Pulling and Inserting Seasons")
            self.season_data()

        # 3. Pulling and Inserting Team, Venue Fixture and Player Data
        
        # team data requires us to pass up an optional parameter like league ID
        # for this, we'll pass up the league_id's for the top5 European leagues
        european_leagues = League.objects.filter(
            # Premier League, La Liga , League 1, Serie A, Primeira Liga
            Q(rapid_league_id=39) | Q(name=140) | Q(rapid_league_id=61) | Q(rapid_league_id=135) | Q(rapid_league_id=94)  
        ).values('name','rapid_league_id')
        if len(european_leagues) == 0:
            print("No european_leagues to loop through.")
            return 

        for league in european_leagues: 
            # Team & Venue Data

            #if Team.objects.count() == 0 or options['override']:
            print("Pulling and Inserting Team Data")
            self.team_data(league_id=league['rapid_league_id'], season=self.season)

            # Fixture Data
            if Fixture.objects.count() == 0 or options['override']:
                print("Pulling and Inserting Fixture Data")
                self.fixture_data(league_id=league['rapid_league_id'], season=self.season)

            # Pull in Players
            #if Player.objects.count() == 0 or options['override']:
            print("Pulling and Inserting Players Data")
            self.player_data(league_id=league['rapid_league_id'], season="2021")

        # 4. Pull Player Stats by Fixture 
        fixtures = Fixture.objects.filter(season=self.season,rapid_fixture_id=868029).values('rapid_fixture_id')
        # for fixture in fixtures:
        #     self.player_fixture_data(fixture_id=fixture['rapid_fixture_id'])

    
    def rapid_api(self, extension, optional_params=False, query_string=False):
        
        url = self.url+extension
        print("url",url)
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
            league = row['league']
            rapid_league_id = league['id']
            name = league['name']
            type = league['name']

            country = row['country']
            country_name = country['name']
            code = country['code'] if country['code'] != None else 'NA'

            # insert data into League table
            League.objects.update_or_create(
                rapid_league_id=rapid_league_id,
                defaults={
                    'id': rapid_league_id,
                    'name': name,
                    'country': country_name,
                    'code': code, 
                    'type': type
                }
            )

    def season_data(self):
        # pull data from rapidAPI with the extension
        response = self.rapid_api('leagues/seasons') 
        for row in response:

            # insert data into Season table
            Season.objects.update_or_create(
                season=row
            )

    def fixture_data(self,league_id,season):
        # pull data from rapidAPI with the extension
        query_string = {'league':league_id,'season':season}
        response = self.rapid_api('fixtures',optional_params=True,query_string=query_string) 
        for row in response:
            
            # fixture 
            fixture = row['fixture']
            rapid_fixture_id = fixture['id']
            fixture_date = fixture['date']
            referee = fixture['referee']
            venue_id = fixture['venue']['id'] 
            try:
                venue_model_id = TeamVenue.objects.get(rapid_venue_id=venue_id).id
            except: 
                print("No Venue Available for venue_id:",venue_id)
                continue

            # league
            league = row['league']
            league_id = league['id'] 
            season = league['season']
            fixture_round = league['round']

            # teams
            teams = row['teams']
            home_team = teams['home']['id']
            away_team = teams['away']['id']
            home_win =  teams['home']['winner']
            away_win =  teams['away']['winner']

            # insert data into Fixture table
            Fixture.objects.update_or_create(
                rapid_fixture_id=rapid_fixture_id,
                defaults={
                    'id': rapid_fixture_id,
                    'fixture_date': fixture_date,
                    'referee': referee,
                    'venue_id': venue_model_id,
                    'league_id': league_id,
                    'season': season,
                    'fixture_round': fixture_round,
                    'home_team_id': home_team,
                    'away_team_id': away_team
                }
            )

            # goals
            goals = row['goals']
            home_goals = goals['home']
            away_goals = goals['away']

            # scores 
            scores = row['score']

            # half time score
            ht_score = scores['halftime']
            home_ht_score = ht_score['home']
            away_ht_score = ht_score['away']

            # full time score
            ft_score = scores['fulltime']
            home_ft_score = ft_score['home']
            away_ft_score = ft_score['away']

            # extra time score
            et_score = scores['fulltime']
            home_et_score = et_score['home']
            away_et_score = et_score['away']

            # extra time penalties
            et_penalties = scores['fulltime']
            home_et_penalities = et_penalties['home']
            away_et_penalities = et_penalties['away']

            # insert data into FixtureStats table
            FixtureStats.objects.update_or_create(
                fixture_id=rapid_fixture_id,
                defaults={
                    'home_win': home_win,
                    'away_win': away_win,
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'home_ht_score': home_ht_score,
                    'away_ht_score': away_ht_score,
                    'home_ft_score': home_ft_score,
                    'away_ft_score': away_ft_score,
                    'home_et_score': home_et_score,
                    'away_et_score': away_et_score,
                    'home_et_penalties': home_et_penalities,
                    'away_et_penalties': away_et_penalities
                }
            )

    def player_fixture_data(self,fixture_id):
        query_string = {'fixture':fixture_id}
        response = self.rapid_api('fixtures/players',optional_params=True,query_string=query_string) 
        for row in response: 
            print("row",row)

    def team_data(self,league_id,season):
        # pull data from rapidAPI with the extension
        query_string = {'league':league_id,'season':season}
        response = self.rapid_api('teams',optional_params=True,query_string=query_string) 
        for row in response:
            
            # team
            team = row['team']
            rapid_team_id = team['id']
            team_name = team['name']
            code = team['code']
            country = team['country']
            national = team['national']
            
            # venue
            venue = row['venue']
            rapid_venue_id = venue['id']
            venue_name = venue['name']
            city = venue['city']
            capacity = venue['capacity']
            surface = venue['surface']

            # insert data into Team table
            team_object, _ = Team.objects.update_or_create(
                rapid_team_id=rapid_team_id,
                defaults={
                    'id': rapid_team_id,
                    'name': team_name,
                    'country': country,
                    'national': national,
                    'code': code
                }
            )

            # insert data into TeamVenue
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

    def player_data(self, league_id, season):
        query_string = {'league':league_id,'season':season}
        response = self.rapid_api('players',optional_params=True,query_string=query_string)
        for row in response: 
            print("row",row)

            # player
            player = row['player']
            rapid_player_id = player['id']
            name = player['name']
            firstname = player['firstname']
            lastname = player['lastname']
            age = player['age']
            dob = player['birth']['date']
            country = player['birth']['country']
            nationality = player['nationality']
            height = player['height']
            weight = player['weight']
            injured = player['injured']

            # insert data into Player table
            player_object, _ = Player.objects.update_or_create(
                rapid_player_id=rapid_player_id,
                defaults={
                    'id': rapid_player_id,
                    'name': name,
                    'firstname': firstname,
                    'lastname': lastname,
                    'age': age,
                    'dob': dob,
                    'nationality': nationality,
                    'country':country,
                    'height': height,
                    'weight': weight,
                    'injured': injured
                }
            )

            # player status
            statistics = row['statistics'][0]
            team_id = statistics['team']['id']
            league_id = statistics['league']['id']

            # games
            appearances = statistics['games']['appearences']
            minutes = statistics['games']['minutes']
            number = statistics['games']['number']
            position = statistics['games']['position']
            rating = statistics['games']['rating']
            captain = statistics['games']['captain']

            # substitutes
            subbed_in = statistics['substitutes']['in']
            subbed_out = statistics['substitutes']['out']
            bench = statistics['substitutes']['bench']

            # shots
            shots = statistics['shots']['total']
            shots_on_target = statistics['shots']['on']
            
            # goals
            goals = statistics['goals']['total']
            conceded = statistics['goals']['conceded']
            assists = statistics['goals']['assists']
            saves = statistics['goals']['saves']

            # passes
            passes = statistics['passes']['total']
            key_passes = statistics['passes']['key']
            accuracy = statistics['passes']['accuracy']

            # tackles
            tackles = statistics['tackles']['total']
            blocks = statistics['tackles']['blocks']
            interceptions = statistics['tackles']['interceptions']

            # duels
            duels = statistics['duels']['total']
            duels_won = statistics['duels']['won']

            # dribbles
            dribbles = statistics['dribbles']['attempts']
            dribble_success = statistics['dribbles']['success']
            dribble_past = statistics['dribbles']['past']

            # fouls
            fouls_drawn = statistics['fouls']['drawn']
            fouls_committed = statistics['fouls']['committed']

            # cards
            yellow_cards = statistics['cards']['yellow']
            yellow_red_cards = statistics['cards']['yellowred']
            red_cards = statistics['cards']['red']

            # penalty
            penalty_won = statistics['penalty']['won']
            penalty_committed = statistics['penalty']['commited']
            penalty_scored = statistics['penalty']['scored']
            penalty_missed = statistics['penalty']['missed']
            penalty_saved = statistics['penalty']['saved']

            # insert data into Team table
            PlayerStats.objects.update_or_create(
                player_id=player_object.id,
                season=season,
                team_id=team_id,
                league_id=league_id,
                defaults={
                    'appearances': appearances,
                    'minutes': minutes,
                    'position': position,
                    'rating': rating,
                    'subbed_in': subbed_in,
                    'subbed_out': subbed_out,
                    'bench':bench,
                    'captain': captain,

                    'shots': shots,
                    'shots_on_target': shots_on_target,
                    'goals': goals,
                    'conceded': conceded,
                    'assists':assists,
                    'saves':saves,

                    'passes': passes,
                    'key_passes': key_passes,
                    'accuracy': accuracy,

                    'tackles': tackles,
                    'blocks':blocks,
                    'interceptions':interceptions,

                    'duels': duels,
                    'duels_won':duels_won,

                    'dribbles':dribbles,
                    'dribble_success':dribble_success,
                    'dribble_past':dribble_past,

                    'fouls_drawn':fouls_drawn,
                    'fouls_committed':fouls_committed,

                    'yellow_cards': yellow_cards,
                    'yellow_red_cards':yellow_red_cards,
                    'red_cards':red_cards,

                    'penalty_won': penalty_won,
                    'penalty_committed':penalty_committed,
                    'penalty_scored':penalty_scored,
                    'penalty_missed':penalty_missed,
                    'penalty_saved':penalty_saved,

                }
            )

# TO DO: 
# INSERT INTO 