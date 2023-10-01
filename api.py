"""
List of API links:
    https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c
"""

import requests
# import pprint
from util import iso_to_dt, load_pkl


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
        
        # if 'weather' not in resp:
        #     print(f"DIDN'T FIND 'WEATHER' IN RESPONSE!")
        #     pp = pprint.PrettyPrinter(indent=4)
        #     pp.pprint(resp)
        
        away, home = [alias[abbrev.strip().capitalize()] for abbrev in resp['shortName'].upper().replace('VS', '@').split('@')]
        
        """Note: 'weather' is a dictionary.
        Important keys: 'displayValue', 'windSpeed', 'temperature', 'lastUpdated', etc. """
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