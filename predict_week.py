"""
TODO: 
    - Deliver betting odds (e.g. +150)
    - Deliver predicted margin of victory
"""

import argparse
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # For pd concat warning

import pandas as pd
from elo import prob_winning, initialize, prob_to_odds, pred_total
from util import load_pkl, save_pkl, validate_ratings, query_team, yes_or_no
from api import query_week


parser = argparse.ArgumentParser(
                    prog='Predict Week',
                    description='This script accepts a schedule as CLI-input, and predicts the outcome for the upcoming games.')
parser.add_argument('-w', '--week', type=int)
parser.add_argument('-y', '--year', type=int, default=2023)


def query_schedule(wk, YEAR=2023, user_input=True):
    """
    Asks the user for games to predict one by one
    """    
    
    savename = f"./data/{YEAR}wk{wk}_predictions.csv"
    
    # First, we'll load the Elo ratings from LAST week
    elos, ortgs, drtgs = initialize(YEAR, week=wk)
    validate_ratings(elos, ortgs, drtgs)
    
    """
    The 'alias' variable is a dictionary that contains nicknames/aliases as keys and true team names as values. 
    All strings, and all uppercase.
    """
    alias_filename = 'alias.pkl'
    alias = load_pkl(alias_filename)
    
    # We'll want to index by team-name, whether we're using an alias or the true name. 
    for team in elos:
        alias[team] = team
    
    savedf = pd.DataFrame(
            columns=['Home Team','Away Team','Home Prob','Away Prob','Home Odds','Away Odds']
        )
    
    # Get schedule 
    if not user_input:
        query = query_week()
        if not (int(meta['week']) == wk and int(meta['season']) == YEAR) or query is None:
            # Got the wrong week from our API request
            print(f"API request failed...\nWe will need you to input the games manually.")
            user_input = True
        else:
            meta, games = query
    # This is not an "else" clause because we change 'user_input' to True if the API request fails
    if user_input:
        games = []
        while True:
            """TODO: Separate the user input from calculations"""
            away = query_team("\nAway Team: ")
            if not away: break
            
            home = query_team("\nHome Team: ")
            if not home: break
            
            games.append({'Away' : away, 'Home' : home})
    
    # Iterate schedule
    for game in games:
        away, home = game['Away'], game['Home']
        home_elo = elos[home]
        away_elo = elos[away]
        
        """
        According to https://fivethirtyeight.com/methodology/how-our-nfl-predictions-work/,
        You can divide EloDiff by 25 in order to get the spread.
        """
        spread = (away_elo - home_elo) / 25  # negative if home team is favored
                
        prob_home_win = prob_winning(home_elo, away_elo)
        prob_away_win = 1 - prob_home_win
        
        home_odds = prob_to_odds(prob_home_win)
        away_odds = prob_to_odds(prob_away_win)
        
        total = pred_total(ortgs[home], drtgs[home], ortgs[away], drtgs[away])
        
        if prob_home_win > prob_away_win:
            print(f"{home} are favored by {abs(spread):.1f} pts ({home_odds})\nExpected point total:\t{total}")
        elif prob_away_win > prob_home_win:
            print(f"{away} are favored by {abs(spread):.1f} pts ({away_odds})\nExpected point total:\t{total}")
        else:
            print(f"Wow! This is a perfectly even matchup!")
            
        entry = pd.DataFrame.from_dict(
            {
                'Home Team' : [home],
                'Away Team' : [away],
                'Home Elo'  : [home_elo],
                'Away Elo'  : [away_elo],
                'Predicted Point Spread'    : [spread],
                'Predicted Total'           : [total],
                'Home Odds' : [home_odds],
                'Away Odds' : [away_odds],
                'Home Prob' : [prob_home_win],
                'Away Prob' : [prob_away_win]
            }
        )
        
        savedf = pd.concat([savedf, entry], ignore_index=True, verify_integrity=True)
        
    savedf.to_csv(savename, index = False)
        

if __name__ == '__main__':
    args = parser.parse_args()
    if args.week is None:
        WEEK = int(input("What week are you making picks for (1-18)?\t"))
    else:
        WEEK = args.week
        
    api_call = yes_or_no("Query games from the internet?")
        
    query_schedule(WEEK, user_input=not api_call)
    