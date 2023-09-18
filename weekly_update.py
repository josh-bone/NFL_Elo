"""
This script allows you to input the weekly scores into a CLI in order to update our data. 
Run it between Tuesday and Thursday during the season.
"""

import time
import pandas as pd
import os
import argparse

from elo import update, initialize, offdef_shift
from util import validate_ratings, yes_or_no


parser = argparse.ArgumentParser(
                    prog='Predict Week',
                    description='This script accepts a schedule as CLI-input, and predicts the outcome for the upcoming games.')
parser.add_argument('-w', '--week', type=int)
parser.add_argument('-y', '--year', type=int, default=2023)

def record_scores(wk):
    """_summary_

    Args:
        wk (_type_): _description_
    """    
    savename = f'./data/{YEAR}wk{wk}_result.csv'
    
    # savedf will hold the results of user input - so we can save it to a .csv later
    if os.path.exists(savename):
        # Sometimes we've already input some of the games, but need to add one more (On Mon. night, for example)
        savedf = pd.read_csv(savename, index_col=0)
    else:
        savedf = pd.DataFrame(
            columns=['Home Team','Away Team','Home Score','Away Score']
            )
    
    print(f"Ready to update scores for {YEAR} week {wk}... \n(Input 'q' to exit)\n")
    
    # Now to begin recording all the games...
    home = 'NaN'
    while True:  # We will 'break' on a 'q' input
        
        # Take inputs
        away = input("Away Team: ")
        if away.lower() == 'q': break
        
        awayscore = input("Away Score: ")
        if awayscore.lower() == 'q': break
        awayscore = int(awayscore)
        
        home = input("Home Team: ")
        if home.lower() == 'q': break
        
        homescore = input("Home Score: ")
        if homescore.lower() == 'q': break
        homescore = int(homescore)
        
        # Format data
        entry = pd.DataFrame.from_dict(
            {'Home Team' : [home], 
                'Away Team' : [away],
                'Home Score': [homescore],
                'Away Score': [awayscore]})
        
        savedf = pd.concat([savedf, entry], ignore_index=True, verify_integrity=True)
        print(savedf)
        print('\n')
        
    savedf.to_csv(savename, index = False)
    
    
def update_elos(wk):
    """
    TODO: This still adds a row even if we already have updated that teams elo 
    
    _summary_

    Args:
        wk (_type_): _description_
    """    
    
    # First, we'll load the Elo ratings from LAST week
    elos, ortgs, drtgs = initialize(YEAR, week=wk)
    validate_ratings(elos, ortgs, drtgs)
    
    print(f"Elo:\n{elos}")
    print(f"ORTGS:\n{ortgs}")
    print(f"DRTGS:\n{drtgs}")
    
    game_results = pd.read_csv(f'./data/{YEAR}wk{wk}_result.csv')
    
    savedf = pd.DataFrame( columns=["Team", "Elo"] )
    
    for ind, row in game_results.iterrows():
        home, away = row['Home Team'], row['Away Team']
        home_old = elos[home]
        away_old = elos[away]
        ortgA, ortgB = ortgs[home], ortgs[away]
        drtgA, drtgB = drtgs[home], drtgs[away]
        points_home, points_away = row['Home Score'], row["Away Score"]
        
        print(f"{away} ({away_old}) @ {home} ({home_old}) \t-\t {points_away}-{points_home}...")
        
        home_new, away_new = update(home_old, away_old, points_home, points_away)
        
        # update
        o_shift, d_shift = offdef_shift(points_home, points_away,
                                        ortgA, ortgB,
                                        drtgA, drtgB)
        
        ortgs[home] = ortgA + o_shift
        ortgs[away] = ortgB - o_shift
        drtgs[home] = drtgA + d_shift
        drtgs[away] = drtgB - d_shift
        
        
        home_entry = pd.DataFrame.from_dict(
            {"Team": [home],
             "Elo" : [home_new],
             "ORTG" : [ortgs[home]],
             "DRTG" : [drtgs[home]]}
            )
        
        away_entry = pd.DataFrame.from_dict(
            {"Team": [away],
             "Elo" : [away_new],
             "ORTG" : [ortgs[away]],
             "DRTG" : [drtgs[away]]}
            )
        
        savedf = pd.concat([savedf, home_entry], ignore_index=True, verify_integrity=True)
        savedf = pd.concat([savedf, away_entry], ignore_index=True, verify_integrity=True)
        
    savename = f'./data/Elo_{YEAR}_week{wk}.csv'
    print(f"Saving to {savename}")
    savedf.to_csv(savename)
    

if __name__ == '__main__':
    
    args = parser.parse_args()
    
    YEAR = args.year
    
    if args.week is None:
        WEEK = int(input("Which week just finished (1-18)? "))
    else:
        WEEK = args.week
    
    if yes_or_no(f"Do you need to input the scores for week {WEEK}?"):
        record_scores(WEEK)
        
    update_elos(WEEK)