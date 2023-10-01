"""
List of API links:
    https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c
"""

import requests
# import pprint
from util import iso_to_dt, load_pkl


def query_scores(WEEKNUM, YEAR=2023):
    """Generates scoreboard for a given week of NFL games

    Args:
        WEEKNUM (int): week [1-18?] (must be finished)
        YEAR (int, optional): _description_. Defaults to 2023.
    """    
    SEASONTYPE = 2  # seasontypes: 1=pre, 2=regular, 3=post, 4=off
    URL = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={YEAR}&seasontype={SEASONTYPE}&week={WEEKNUM}'
    r = requests.get(url=URL)
    resp = r.json()

    games = []
    for game in resp['events']:
        home, away = None, None
        for competitor in game['competitions'][0]['competitors']:
            tm = competitor['team']['name']
            score = int(competitor['score'])
            if competitor['homeAway'] == 'home':
                home = tm
                homescore = score
            elif competitor['homeAway'] == 'away':
                away = tm
                awayscore = score
        assert home is not None and away is not None, "Incomplete game"
        games.append({"Home" : home,
                        "Home Score" : homescore, 
                        "Away" : away,
                        "Away Score" : awayscore})
        
    return(games)
        

def query_week(alias_filename = 'alias.pkl'):
    """
    TODO: See why there's only weather info for *some* games - maybe it has to be same-day?
    
    Returns a list of dictionaries 
        - one for each of the upcoming games in the current week
    """    
    meta, links = query_game_links()

    alias = load_pkl(alias_filename)

    games = []
    for link in links:
        r = requests.get(url=link)
        resp = r.json()
        
        away, home = [alias[abbrev.strip().capitalize()] for abbrev in resp['shortName'].upper().replace('VS', '@').split('@')]
        
        """Note: 'weather' is a dictionary.
        Important keys: 'displayValue', 'windSpeed', 'temperature', 'lastUpdated', etc. """
        
        # if 'weather' not in resp:
        #     print(f"DIDN'T FIND 'WEATHER' IN RESPONSE!")
        #     pp = pprint.PrettyPrinter(indent=4)
        #     pp.pprint(resp)
        
        # weather = resp['weather']  
        
        # weather_time = iso_to_dt(weather['lastUpdated'])  # this is important bc we want to know if this weather report is near game-time
        gametime = iso_to_dt(resp['date'])
        
        # games.append({'Away' : away,
        #               'Home' : home,
        #               'Weather': weather['displayValue'],
        #               'Wind' : weather['windSpeed'],
        #               'Rain' : weather['precipitation'],
        #               'Game Time' : gametime,
        #               'Weather Time' : weather_time})
        
        games.append({'Away' : away,
                      'Home' : home,
                      'Time' : gametime})
        
    return(meta, games)

def query_game_links():
    """Gets all links for the CURRENT WEEK's games
    """    
    
    # The following URL contains a summary of the current week 
    url = 'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events'
    
    r = requests.get(url=url)
    resp = r.json()
    
    links = [el['$ref'] for el in resp['items']]
    meta = resp['$meta']['parameters']  # seasontypes: 1=pre, 2=regular, 3=post, 4=off
    
    return(meta, links)