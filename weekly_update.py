"""
This script allows you to input the weekly scores into a CLI in order to update our data. 
Run it between Tuesday and Thursday during the season.
"""

import time
import pandas as pd
import os

from elo import update, initialize_elo

YEAR = 2023

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
    elos = initialize_elo(YEAR, week=wk)
    
    game_results = pd.read_csv(f'./data/{YEAR}wk{wk}_result.csv')
    
    savedf = pd.DataFrame( columns=["Team", "Elo"] )
    
    for ind, row in game_results.iterrows():
        home, away = row['Home Team'], row['Away Team']
        home_old = elos[home]
        away_old = elos[away]
        points_home, points_away = row['Home Score'], row["Away Score"]
        
        print(f"{away} ({away_old}) @ {home} ({home_old}) \t-\t {points_away}-{points_home}...")
        
        home_new, away_new = update(home_old, away_old, points_home, points_away)
        
        print(f"{home} Elo changed from {home_old:.0f} to {home_new:.0f}")
        print(f"{away} Elo changed from {away_old:.0f} to {away_new:.0f}")
        
        home_entry = pd.DataFrame.from_dict(
            {"Team": [row['Home Team']],
             "Elo" : [home_new]}
            )
        
        away_entry = pd.DataFrame.from_dict(
            {"Team": [row['Away Team']],
             "Elo" : [away_new]}
            )
        
        savedf = pd.concat([savedf, home_entry], ignore_index=True, verify_integrity=True)
        savedf = pd.concat([savedf, away_entry], ignore_index=True, verify_integrity=True)
        
    savename = f'./data/Elo_{YEAR}_week{wk}.csv'
    print(f"Saving to {savename}")
    savedf.to_csv(savename)

if __name__ == '__main__':
    WEEK = int(input("What week is it (1-18)? "))
    record_scores(WEEK)
    update_elos(WEEK)