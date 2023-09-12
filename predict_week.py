"""
TODO: 
    - Deliver betting odds (e.g. +150)
    - Deliver predicted margin of victory
"""

import os
import pandas as pd
from elo import prob_winning, initialize_elo, prob_to_odds

def query_schedule(wk, YEAR = 2023):
    """
    Asks the user for games to predict one by one
    """    
    
    savename = f"./data/{YEAR}wk{wk}_predictions.csv"
    
    # First, we'll load the Elo ratings from LAST week
    elos = initialize_elo(YEAR, week=wk)
    
    # savedf will hold the prediction results - so we can save it to a .csv later
    if os.path.exists(savename):
        # Sometimes we've already input some of the games, but need to add one more (On Mon. night, for example)
        savedf = pd.read_csv(savename, index_col=0)
    else:
        savedf = pd.DataFrame(
            columns=['Home Team','Away Team','Home Prob','Away Prob','Home Odds','Away Odds']
        )
    
    # Take inputs
    while True:
        
        away = input("Away Team: ")
        if away.lower() == 'q': break
        
        home = input("Home Team: ")
        if home.lower() == 'q': break
        
        home_elo = elos[home]
        away_elo = elos[away]
        
        print(f"Predicting the result of {away} ({away_elo:.0f}) @ {home} ({home_elo:.0f})...")
        
        prob_home_win = prob_winning(home_elo, away_elo)
        prob_away_win = 1 - prob_home_win
        
        home_odds = prob_to_odds(prob_home_win)
        away_odds = prob_to_odds(prob_away_win)
        
        if prob_home_win > prob_away_win:
            print(f"{home} are favored ({home_odds}), with a {prob_home_win*100:.2f}% chance of winning\n")
        elif prob_away_win > prob_home_win:
            print(f"{away} are favored ({away_odds}), with a {prob_away_win*100:.2f}% chance of winning\n")
        else:
            print(f"Wow! This is a perfectly even matchup!")
            
        entry = pd.DataFrame.from_dict(
            {
                'Home Team' : [home],
                'Away Team' : [away],
                'Home Elo'  : [home_elo],
                'Away Elo'  : [away_elo],
                'Home Odds' : [home_odds],
                'Away Odds' : [away_odds],
                'Home Prob' : [prob_home_win],
                'Away Prob' : [prob_away_win]
            }
        )
        
        savedf = pd.concat([savedf, entry], ignore_index=True, verify_integrity=True)
        # print(savedf)
        # print('\n')
        
    savedf.to_csv(savename, index = False)
        

if __name__ == '__main__':
    # YEAR = 2023
    WEEK = int(input("What week are you making picks for (1-18)? "))
    query_schedule(WEEK)
    