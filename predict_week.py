"""
TODO: 
    - Deliver betting odds (e.g. +150)
    - Deliver predicted margin of victory
"""

import os
import argparse
import pickle as pkl

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # For pd concat warning

import pandas as pd
from elo import prob_winning, initialize_elo, prob_to_odds

parser = argparse.ArgumentParser(
                    prog='Predict Week',
                    description='This script accepts a schedule as CLI-input, and predicts the outcome for the upcoming games.')
parser.add_argument('-w', '--week', type=int)
parser.add_argument('-y', '--year', type=int)


def load_pkl(fname):
    """Loads a dictionary from a .pkl file. 
    Returns this dictionary, if the file exists, or an empty one if not.

    Args:
        fname (str): name of the .pkl file, including full path if it is not in the CWD.
    """    
    if not os.path.exists(fname):
        dic = {}  # We are going to save nicknames here to make CLI-input easier 
    else:
        with open(fname, 'rb') as f:
            dic = pkl.load(f)
    return(dic)

def save_pkl(obj, fname):
    with open(fname, 'wb') as f:
        pkl.dump(obj, f)

def query_schedule(wk, YEAR = 2023):
    """
    Asks the user for games to predict one by one
    """    
    
    savename = f"./data/{YEAR}wk{wk}_predictions.csv"
    
    # First, we'll load the Elo ratings from LAST week
    elos = initialize_elo(YEAR, week=wk)
    
    """
    The 'alias' variable is a dictionary that contains nicknames/aliases as keys and true team names as values. 
    All strings, and all uppercase.
    """
    alias_filename = 'alias.pkl'
    alias = load_pkl(alias_filename)
    
    # We'll want to index by team-name, whether we're using an alias or the true name. 
    for team in elos:
        alias[team] = team
    
    valid = {"y":True, "yes":True, "n":False, "no":False}
    
    """TODO: allow for piece-by-piece input"""
    # # savedf will hold the prediction results - so we can save it to a .csv later
    # if os.path.exists(savename):
    #     # Sometimes we've already input some of the games, but need to add one more (On Mon. night, for example)
    #     savedf = pd.read_csv(savename, index_col=0)
    # else:
    #     savedf = pd.DataFrame(
    #         columns=['Home Team','Away Team','Home Prob','Away Prob','Home Odds','Away Odds']
    #     )
    
    savedf = pd.DataFrame(
            columns=['Home Team','Away Team','Home Prob','Away Prob','Home Odds','Away Odds']
        )
    
    
    # Take inputs
    while True:
        
        away = input("\nAway Team: ").capitalize()
        if away.lower() == 'q': break
        elif away in alias:
            away = alias[away]
        # TODO: Change away to alias[away] 
        elif away not in elos:
            print(f"I didn't recognize the team {away}...")
            yn = input(f"Would you like to save {away} as an alias for an NFL team? [y/n] ").casefold()
            if valid[yn]:
                true_team = input(f"For which team is {away} an alias? ").capitalize()
                assert true_team in elos
                alias[away] = true_team.capitalize()
            else:
                assert False, "Re-input is not yet implemented"
        else: assert False, "Unexpected error. Please reach out to the developer."
        away = alias[away]
        
        home = input("\nHome Team: ").capitalize()
        if home.casefold() == 'q': break
        elif home in alias:
            home = alias[home]
        # TODO: Change home to alias[home] 
        elif home not in elos:
            print(f"I didn't recognize the team {home}...")
            yn = input(f"Would you like to save {home} as an alias for an NFL team? [y/n] ").casefold()
            if valid[yn]:
                true_team = input(f"For which team is {home} an alias? ").capitalize()
                assert true_team in elos
                alias[home] = true_team.capitalize()
            else:
                assert False, "Re-input is not yet implemented"
        else: assert False, "Unexpected error. Please reach out to the developer."
        home = alias[home]
        
        home_elo = elos[home]
        away_elo = elos[away]
        
        """
        According to https://fivethirtyeight.com/methodology/how-our-nfl-predictions-work/,
        You can divide EloDiff by 25 in order to get the spread.
        """
        spread = (away_elo - home_elo) / 25  # negative if home team is favored
        
        print(f"Predicting the result of {away} ({away_elo:.0f}) @ {home} ({home_elo:.0f})...")
        
        prob_home_win = prob_winning(home_elo, away_elo)
        prob_away_win = 1 - prob_home_win
        
        home_odds = prob_to_odds(prob_home_win)
        away_odds = prob_to_odds(prob_away_win)
        
        if prob_home_win > prob_away_win:
            print(f"{home} are favored by {abs(spread):.1f} pts ({home_odds}), with a {prob_home_win*100:.2f}% chance of winning\n")
        elif prob_away_win > prob_home_win:
            print(f"{away} are favored by {abs(spread):.1f} pts ({away_odds}), with a {prob_away_win*100:.2f}% chance of winning\n")
        else:
            print(f"Wow! This is a perfectly even matchup!")
            
        entry = pd.DataFrame.from_dict(
            {
                'Home Team' : [home],
                'Away Team' : [away],
                'Home Elo'  : [home_elo],
                'Away Elo'  : [away_elo],
                'Spread'    : [spread],
                'Home Odds' : [home_odds],
                'Away Odds' : [away_odds],
                'Home Prob' : [prob_home_win],
                'Away Prob' : [prob_away_win]
            }
        )
        
        savedf = pd.concat([savedf, entry], ignore_index=True, verify_integrity=True)
        
    savedf.to_csv(savename, index = False)
    save_pkl(alias, alias_filename)
        

if __name__ == '__main__':
    args = parser.parse_args()
    if args.week is None:
        WEEK = int(input("What week are you making picks for (1-18)? "))
    else:
        WEEK = args.week
    query_schedule(WEEK)
    