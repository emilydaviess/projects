# main.py
from football.models import (
    League,
    Team,
    TeamVenue,
    TeamSeason,
    Season,
    Fixture,
    FixtureStats,
    Player,
    PlayerStats,
    FixturePlayerStats,
)
from football.commands import BaseCommand
from django.db.models import Q
from django.conf import settings
from football.functions import (
    rapid_api,
    handle_pagination,
    calculate_season,
)


class Command(BaseCommand):
    help = "Pull raw football data from RapidAPI"
    # https://rapidapi.com/api-sports/api/api-football
    # https://rapidapi.com/Wolf1984/api/football-xg-statistics (XG)

    def add_arguments(self, parser):
        parser.add_argument("--override", dest="override", action="store_true")
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **kwargs):

        self.headers = {
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
            "X-RapidAPI-Key": settings.X_RAPIDAPI_KEY,
        }
        self.url = "https://api-football-v1.p.rapidapi.com/v3/"

        # --startdate and --enddate get passed in via the command kwargs and are optional, if they're not passed in, we'll default to the current date
        self.startdate, self.enddate = self.check_date_formatting(**kwargs)
        self.total_pages = 1

        print("Running for startdate:", self.startdate, "enddate:", self.enddate)

        # if the month is > July, current_season is the current year, else it's the previous year
        startdate_season = calculate_season(self.startdate)
        enddate_season = calculate_season(self.enddate)

        self.startdate = self.startdate.format("YYYY-MM-DD")
        self.enddate = self.enddate.format("YYYY-MM-DD")

        # get all seasons between startdate and enddate for running
        self.seasons = Season.objects.filter(
            season__gte=startdate_season,
            season__lte=enddate_season,
        ).values_list("season", flat=True)

        print("self.seasons", self.seasons)

        # 1. pull and insert league data i.e. Premier League, La Liga
        # we don't expect Leagues to change often, so we'll only run this if the League table is empty, or if we pass up the optional parameter --override
        if League.objects.count() == 0 or kwargs["override"]:
            self.print_info("Pulling and Inserting League Data")
            self.pull_league_data()

        # 2. pull and insert seasons i.e. 2022
        # we don't expect Seasons to change often, so we'll only run this if the Season table is empty, or if we pass up the optional parameter --override
        if Season.objects.count() == 0 or kwargs["override"]:
            self.print_info("Pulling and Inserting Seasons")
            self.pull_season_data()

        # 3. pulling and Inserting team, venue fixture and player data

        # team data requires us to pass up a parameter like league ID
        # we'll pass up the league_id's for the top5 European leagues
        european_leagues = League.objects.filter(
            # Premier League, La Liga , League 1, Serie A, Primeira Liga
            Q(rapid_league_id=39)
            # | Q(name=140) | Q(rapid_league_id=61) | Q(rapid_league_id=135) | Q(rapid_league_id=94)
        ).values("name", "rapid_league_id")

        for season in self.seasons:
            season_obj = Season.objects.get(season=season)
            print("season:", season)

            for league in european_leagues:
                print("league:", league)

                league_id = league["rapid_league_id"]

                # team & venue data: only need to run this once a season, or if we pass up the optional parameter --override
                if (
                    TeamSeason.objects.filter(
                        league_id=league_id, season_id=season_obj.id
                    ).count()
                    == 0
                    or kwargs["override"]
                ):
                    print("Pulling and Inserting Team Data")
                    self.pull_team_data(league_id=league_id, season_obj=season_obj)

                # players & general player data: only need to run this once a season, or if we pass up the optional parameter --override
                teams = (
                    TeamSeason.objects.filter(
                        league_id=league_id, season_id=season_obj.id
                    )
                    .values("team_id")
                    .distinct()
                )
                for team in teams:
                    team_id = team["team_id"]
                    print(
                        "pulling player data for team:",
                        team_id,
                        "& league_id:",
                        league_id,
                        "& season:",
                        season_obj.season,
                    )
                    if (
                        PlayerStats.objects.filter(
                            league_id=league_id,
                            season_id=season_obj.id,
                            team_id=team_id,
                        ).count()
                        == 0
                        or kwargs["override"]
                    ):
                        self.print_info(
                            "Pulling and Inserting Players Data for Team:", team_id
                        )
                        self.pull_player_data(
                            league_id=league_id, team_id=team_id, season_obj=season_obj
                        )

                # fixture data: this will need updating every week, hence we'll pass a startdate to the rapid api endpoint to only pull fixtures from that date

                fixtures = Fixture.objects.filter(
                    league_id=league_id,
                    fixture_date__gte=self.startdate,
                    fixture_date__lte=self.enddate,
                )
                total_count = fixtures.count()
                null_referee_count = fixtures.filter(
                    referee__isnull=True
                ).count()  # you can pull fixtures in advance but with no fixture information, hence we'd want to update this data

                if total_count == 0 or null_referee_count > 0 or kwargs["override"]:
                    self.print_info("Pulling and Inserting Fixture Data")
                    self.pull_fixture_data(league_id=league_id, season_obj=season_obj)

                # player stats by fixture: this will need updating every week, hence we'll only pull fixtures between the startdate and enddate
                fixtures = Fixture.objects.filter(
                    league_id=league_id,
                    fixture_date__gte=self.startdate,
                    fixture_date__lte=self.enddate,
                ).values("rapid_fixture_id")
                print("fixtures count:", fixtures.count())

                for fixture in fixtures:
                    fixture_id = fixture["rapid_fixture_id"]
                    self.pull_player_fixture_data(fixture_id=fixture_id)

        self.print_success("Finished pulling and inserting player data")

    def pull_league_data(self):

        response, paging = rapid_api(self, "leagues")

        for row in response:
            league = row["league"]
            rapid_league_id = league["id"]
            name = league["name"]
            type = league["name"]

            country = row["country"]
            country_name = country["name"]
            code = country["code"] if country["code"] != None else "NA"

            # insert data into League table
            League.objects.update_or_create(
                rapid_league_id=rapid_league_id,
                defaults={
                    "id": rapid_league_id,
                    "name": name,
                    "country": country_name,
                    "code": code,
                    "type": type,
                },
            )

    def pull_season_data(self):
        # pull data from rapidAPI with the extension
        response, paging = rapid_api(self, extension="seasons")

        for row in response:
            # insert data into Season table
            Season.objects.update_or_create(season=row)

    def pull_fixture_data(self, league_id, season_obj):
        # pull data from rapidAPI with the extension
        query_string = {
            "league": league_id,
            "season": season_obj.season,
            "from": self.startdate,
            "to": self.enddate,
        }
        response, paging = rapid_api(
            self, extension="fixtures", optional_params=True, query_string=query_string
        )
        if not response or response is None:
            self.print_warning("No response returned from RapidAPI.")
            return

        for row in response:
            # fixture
            fixture = row["fixture"]
            rapid_fixture_id = fixture["id"]
            fixture_date = fixture["date"]
            fixture_timestamp = fixture["timestamp"]
            fixture_timezone = fixture["timezone"]
            referee = fixture["referee"]
            venue_id = fixture["venue"]["id"]
            try:
                venue_model_id = TeamVenue.objects.get(rapid_venue_id=venue_id).id
            except:
                print("No Venue Available for venue_id:", venue_id)
                continue

            # league
            league = row["league"]
            league_id = league["id"]
            season = league["season"]
            season_id = Season.objects.get(season=season).id
            fixture_round = league["round"]

            # teams
            teams = row["teams"]
            home_team = teams["home"]["id"]
            away_team = teams["away"]["id"]

            # insert data into Fixture table
            Fixture.objects.update_or_create(
                rapid_fixture_id=rapid_fixture_id,
                defaults={
                    "id": rapid_fixture_id,
                    "fixture_date": fixture_date,
                    "timestamp": fixture_timestamp,
                    "timezone": fixture_timezone,
                    "referee": referee,
                    "venue_id": venue_model_id,
                    "league_id": league_id,
                    "season_id": season_id,
                    "fixture_round": fixture_round,
                    "home_team_id": home_team,
                    "away_team_id": away_team,
                },
            )
            # game result
            home_win = teams["home"]["winner"]
            away_win = teams["away"]["winner"]
            draw = 1 if home_win is None and away_win is None else 0

            # goals
            goals = row["goals"]
            home_goals = goals["home"]
            away_goals = goals["away"]

            # scores
            scores = row["score"]

            # half time score
            ht_score = scores["halftime"]
            home_ht_score = ht_score["home"]
            away_ht_score = ht_score["away"]

            # full time score
            ft_score = scores["fulltime"]
            home_ft_score = ft_score["home"]
            away_ft_score = ft_score["away"]

            # extra time score
            et_score = scores["extratime"]
            home_et_score = et_score["home"]
            away_et_score = et_score["away"]

            # extra time penalties
            et_penalties = scores["penalty"]
            home_et_penalities = et_penalties["home"]
            away_et_penalities = et_penalties["away"]

            # insert data into FixtureStats table
            FixtureStats.objects.update_or_create(
                fixture_id=rapid_fixture_id,
                defaults={
                    "home_win": home_win,
                    "away_win": away_win,
                    "draw": draw,
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "home_ht_score": home_ht_score,
                    "away_ht_score": away_ht_score,
                    "home_ft_score": home_ft_score,
                    "away_ft_score": away_ft_score,
                    "home_et_score": home_et_score,
                    "away_et_score": away_et_score,
                    "home_et_penalties": home_et_penalities,
                    "away_et_penalties": away_et_penalities,
                },
            )

    def pull_team_data(self, league_id, season_obj):
        # pull data from rapidAPI with the extension
        query_string = {
            "league": league_id,
            "season": season_obj.season,
        }
        response, paging = rapid_api(
            self, extension="teams", optional_params=True, query_string=query_string
        )

        for row in response:
            # team
            team = row["team"]
            rapid_team_id = team["id"]
            team_name = team["name"]
            code = team["code"]
            country = team["country"]
            national = team["national"]

            # venue
            venue = row["venue"]
            rapid_venue_id = venue["id"]
            venue_name = venue["name"]
            city = venue["city"]
            capacity = venue["capacity"]
            surface = venue["surface"]

            # insert data into Team table
            team_object, _ = Team.objects.update_or_create(
                rapid_team_id=rapid_team_id,
                defaults={
                    "id": rapid_team_id,
                    "name": team_name,
                    "country": country,
                    "national": national,
                    "code": code,
                    "league_id": league_id,
                },
            )

            # insert data into TeamVenue
            TeamVenue.objects.update_or_create(
                team_id=team_object.id,
                rapid_venue_id=rapid_venue_id,
                defaults={
                    "name": venue_name,
                    "city": city,
                    "capacity": capacity,
                    "surface": surface,
                },
            )

            TeamSeason.objects.update_or_create(
                team_id=team_object.id, league_id=league_id, season_id=season_obj.id
            )

    def pull_player_data(self, league_id, team_id, season_obj, api_paging=False):
        # players part of the API is paginated, so we'll need to handle that
        query_string = {"league": league_id, "season": season_obj.season}
        if api_paging:
            query_string = {
                "league": league_id,
                "team": team_id,
                "season": season_obj.season,
                "page": api_paging,
            }

        response, paging = rapid_api(
            self, extension="players", optional_params=True, query_string=query_string
        )

        # paging.get("total", 1) returns the value of paging["total"] if it exists
        self.total_pages = paging.get("total", 1) if paging else self.total_pages
        print("total_pages:", self.total_pages)

        if api_paging >= self.total_pages:
            self.print_info(
                f"No more pages to loop through, pulled {api_paging}:{self.total_pages} pages from API."
            )
            return

        # we're getting instances in which the response is None, so we'll need to handle that
        if not response or response is None:
            self.print_warning("Rapid API response returned None.")
            # re-call the function with the next page
            self.pull_player_data(
                league_id=league_id,
                team_id=team_id,
                season_obj=season_obj,
                api_paging=api_paging + 1,
            )

        for row in response:
            # player
            player = row["player"]
            rapid_player_id = player["id"]
            name = player["name"]
            firstname = player["firstname"]
            lastname = player["lastname"]
            age = player["age"]
            dob = player["birth"]["date"]
            country = player["birth"]["country"]
            nationality = player["nationality"]
            height = player["height"]
            weight = player["weight"]
            injured = player["injured"]

            # insert data into Player table
            player_object, _ = Player.objects.update_or_create(
                rapid_player_id=rapid_player_id,
                defaults={
                    "id": rapid_player_id,
                    "name": name,
                    "firstname": firstname,
                    "lastname": lastname,
                    "age": age,
                    "dob": dob,
                    "nationality": nationality,
                    "country": country,
                    "height": height,
                    "weight": weight,
                    "injured": injured,
                },
            )

            # player status
            statistics = row["statistics"][0]
            team_id = statistics["team"]["id"]
            league_id = statistics["league"]["id"]

            # games
            appearances = statistics["games"]["appearences"]
            minutes = statistics["games"]["minutes"]
            number = statistics["games"]["number"]
            position = statistics["games"]["position"]
            rating = statistics["games"]["rating"]
            captain = statistics["games"]["captain"]

            # substitutes
            subbed_in = statistics["substitutes"]["in"]
            subbed_out = statistics["substitutes"]["out"]
            bench = statistics["substitutes"]["bench"]

            # shots
            shots = statistics["shots"]["total"]
            shots_on_target = statistics["shots"]["on"]

            # goals
            goals = statistics["goals"]["total"]
            conceded = statistics["goals"]["conceded"]
            assists = statistics["goals"]["assists"]
            saves = statistics["goals"]["saves"]

            # passes
            passes = statistics["passes"]["total"]
            key_passes = statistics["passes"]["key"]
            accuracy = statistics["passes"]["accuracy"]

            # tackles
            tackles = statistics["tackles"]["total"]
            blocks = statistics["tackles"]["blocks"]
            interceptions = statistics["tackles"]["interceptions"]

            # duels
            duels = statistics["duels"]["total"]
            duels_won = statistics["duels"]["won"]

            # dribbles
            dribbles = statistics["dribbles"]["attempts"]
            dribble_success = statistics["dribbles"]["success"]
            dribble_past = statistics["dribbles"]["past"]

            # fouls
            fouls_drawn = statistics["fouls"]["drawn"]
            fouls_committed = statistics["fouls"]["committed"]

            # cards
            yellow_cards = statistics["cards"]["yellow"]
            yellow_red_cards = statistics["cards"]["yellowred"]
            red_cards = statistics["cards"]["red"]

            # penalty
            penalty_won = statistics["penalty"]["won"]
            penalty_committed = statistics["penalty"]["commited"]
            penalty_scored = statistics["penalty"]["scored"]
            penalty_missed = statistics["penalty"]["missed"]
            penalty_saved = statistics["penalty"]["saved"]

            # insert data into Team table
            PlayerStats.objects.update_or_create(
                player_id=player_object.id,
                season_id=season_obj.id,
                team_id=team_id,
                league_id=league_id,
                defaults={
                    "appearances": appearances,
                    "minutes": minutes,
                    "position": position,
                    "rating": rating,
                    "subbed_in": subbed_in,
                    "subbed_out": subbed_out,
                    "bench": bench,
                    "captain": captain,
                    "shots": shots,
                    "shots_on_target": shots_on_target,
                    "goals": goals,
                    "conceded": conceded,
                    "assists": assists,
                    "saves": saves,
                    "passes": passes,
                    "key_passes": key_passes,
                    "accuracy": accuracy,
                    "tackles": tackles,
                    "blocks": blocks,
                    "interceptions": interceptions,
                    "duels": duels,
                    "duels_won": duels_won,
                    "dribbles": dribbles,
                    "dribble_success": dribble_success,
                    "dribble_past": dribble_past,
                    "fouls_drawn": fouls_drawn,
                    "fouls_committed": fouls_committed,
                    "yellow_cards": yellow_cards,
                    "yellow_red_cards": yellow_red_cards,
                    "red_cards": red_cards,
                    "penalty_won": penalty_won,
                    "penalty_committed": penalty_committed,
                    "penalty_scored": penalty_scored,
                    "penalty_missed": penalty_missed,
                    "penalty_saved": penalty_saved,
                },
            )

        # if there are more pages, we'll need to loop through them
        handle_pagination(
            paging, self.pull_player_data, league_id=league_id, season_obj=season_obj
        )

    def pull_player_fixture_data(self, fixture_id):
        query_string = {"fixture": fixture_id}
        response, paging = rapid_api(
            self,
            extension="fixtures/players",
            optional_params=True,
            query_string=query_string,
        )
        if not response or response is None:
            self.print_warning("No response returned from RapidAPI.")
            return

        for row in response:
            team_id = row["team"]["id"]
            players = row["players"]
            for player in players:
                player_id = player["player"]["id"]

                player_stats = player["statistics"][0]

                # games
                player_stats_games = player_stats["games"]
                minutes = player_stats_games["minutes"]
                number = player_stats_games["number"]
                position = player_stats_games["position"]
                rating = player_stats_games["rating"]
                captain = player_stats_games["captain"]

                # in-game stats
                offsides = player_stats["offsides"]
                shots = player_stats["shots"]["total"]
                shots_on_target = player_stats["shots"]["on"]
                goals = player_stats["goals"]["total"]
                assists = player_stats["goals"]["assists"]
                saves = player_stats["goals"]["saves"]
                conceded = player_stats["goals"]["conceded"]

                passes = player_stats["passes"]["total"]
                key_passes = player_stats["passes"]["key"]
                accuracy = player_stats["passes"]["accuracy"]

                tackles = player_stats["tackles"]["total"]
                blocks = player_stats["tackles"]["blocks"]
                interceptions = player_stats["tackles"]["interceptions"]

                duels = player_stats["duels"]["total"]
                duels_won = player_stats["duels"]["won"]

                dribbles = player_stats["dribbles"]["attempts"]
                dribble_success = player_stats["dribbles"]["success"]
                dribble_past = player_stats["dribbles"]["past"]

                fouls_drawn = player_stats["fouls"]["drawn"]
                fouls_committed = player_stats["fouls"]["committed"]

                yellow_cards = player_stats["cards"]["yellow"]
                red_cards = player_stats["cards"]["red"]

                penalty_won = player_stats["penalty"]["won"]
                penalty_committed = player_stats["penalty"]["commited"]
                penalty_scored = player_stats["penalty"]["scored"]
                penalty_missed = player_stats["penalty"]["missed"]
                penalty_saved = player_stats["penalty"]["saved"]

                try:
                    FixturePlayerStats.objects.update_or_create(
                        player_id=player_id,
                        fixture_id=fixture_id,
                        team_id=team_id,
                        defaults={
                            "minutes": minutes,
                            "number": number,
                            "position": position,
                            "rating": rating,
                            "captain": captain,
                            "offsides": offsides,
                            "shots": shots,
                            "shots_on_target": shots_on_target,
                            "goals": goals,
                            "assists": assists,
                            "saves": saves,
                            "conceded": conceded,
                            "passes": passes,
                            "key_passes": key_passes,
                            "accuracy": accuracy,
                            "tackles": tackles,
                            "blocks": blocks,
                            "interceptions": interceptions,
                            "duels": duels,
                            "duels_won": duels_won,
                            "dribbles": dribbles,
                            "dribble_success": dribble_success,
                            "dribble_past": dribble_past,
                            "fouls_drawn": fouls_drawn,
                            "fouls_committed": fouls_committed,
                            "yellow_cards": yellow_cards,
                            "red_cards": red_cards,
                            "penalty_won": penalty_won,
                            "penalty_committed": penalty_committed,
                            "penalty_scored": penalty_scored,
                            "penalty_missed": penalty_missed,
                            "penalty_saved": penalty_saved,
                        },
                    )
                except Exception as e:
                    self.print_failure(
                        f"Error inserting FixturePlayerStats for player_id: {player_id} and fixture_id: {fixture_id} and team_id: {team_id} with error: {e}"
                    )
