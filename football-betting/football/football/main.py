import requests
import django
django.setup()
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from models.models import League

headers = {
	"X-RapidAPI-Key": "9e42c082bcmshf010546ab6cbf61p10d694jsnd6bffa46a932",
	"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

url = "https://api-football-v1.p.rapidapi.com/v3/"

# pull in the leagues
extension = "leagues"
url = url+extension

response = requests.get(url, headers=headers).json()
leagues = response['response']

for row in leagues:
    # see example_responses.leagues.json for example responses

    league = row['league']
    rapid_league_id = league['id']
    name = league['name']

    country = row['country']
    country_name = country['name']
    code = country['code'] if country['code'] != None else 'NA'

    print("name:",name, country_name)

    # insert data into League table
    League.objects.update_or_create(
        name=name,
        defaults={
            'rapid_league_id': rapid_league_id,
            'country_name': country_name,
            'code': code
        }
    )


