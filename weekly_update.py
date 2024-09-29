"""
This script allows you to input the weekly scores into a CLI in order to update our data. 
Run it between Tuesday and Thursday during the season.
"""

import time
import pandas as pd
import os
import argparse

from elo import update, initialize_ratings, offdef_shift
from util import validate_ratings, yes_or_no, load_pkl, query_team
from api import query_scores


parser = argparse.ArgumentParser(
                    prog='Predict Week',
                    description='This script accepts a schedule as CLI-input, and predicts the outcome for the upcoming games.')
parser.add_argument('-w', '--week')
parser.add_argument('-y', '--year', type=int, default=2023)

def input_scores():
    """Asks the user to input the results from each game
    Returns a pandas dataframe containing all results
    """    
    while True:  # We will 'break' on a 'q' input
        # Take inputs
        away = query_team("Away Team: ")
        if not away: break
        
        awayscore = input("Away Score: ")
        if awayscore.lower() == 'q': break
        awayscore = int(awayscore)
        
        home = query_team("Home Team: ")
        if not home: break
        
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
    return(savedf)

def record_scores(wk, year=2023, user_input=False):
    """_summary_

    Args:
        wk (_type_): _description_
    """    
    savename = f'./data/{year}wk{wk}_result.csv'
    
    # savedf will hold the results of user input - so we can save it to a .csv later
    if os.path.exists(savename):
        # Sometimes we've already input some of the games, but need to add one more (On Mon. night, for example)
        savedf = pd.read_csv(savename, index_col=0)
    else:
        savedf = pd.DataFrame(
            columns=['Home Team','Away Team','Home Score','Away Score']
            )
    
    print(f"Ready to update scores for {year} week {wk}... \n(Input 'q' to exit)\n")
    
    # Now to begin recording all the games...
    home = 'NaN'
    
    if not user_input:
        query = query_scores(wk, YEAR=year)
        savedf = pd.DataFrame.from_records(query)
    else:
        savedf = input_scores()
        
    print(savedf)
    print('\n')
    savedf.to_csv(savename, index = False)
    
    
def update_elos(wk, year=2023):
    """
    TODO: 
        I think this function should start at week 0 and move all the way to current week.
        This way, if I update some code (e.g. change the ORTG/DRTG strategy), everything will use that same updated strategy.
        Currently, I'd have to run this 4 separate times to get updated week 4 ratings.
        
    Args:
        wk (_type_): _description_
    """    
    
    # First, we'll load the Elo ratings from LAST week
    elos, ortgs, drtgs = initialize_ratings(year, week=wk)
    validate_ratings(elos, ortgs, drtgs)
    
    game_results = pd.read_csv(f'./data/{year}wk{wk}_result.csv')
    
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
        
    '''If a team was on a bye last week, we still need to include them in savedf!'''
    print(f"Calling initialize_ratings(year=year, week=wk-1)")
    former_elos, former_ortgs, former_drtgs = initialize_ratings(year=year, week=wk-1)
    for tm in former_elos:    
        if tm not in savedf["Team"]:
            print(f"{tm} is on a bye week - copying their elo from last week")
            bye_entry = pd.DataFrame.from_dict(
            {"Team": [tm],
             "Elo" : [former_elos[tm]],
             "ORTG" : [former_ortgs[tm]],
             "DRTG" : [former_drtgs[tm]]}
            )
            savedf = pd.concat([savedf, bye_entry], ignore_index=True, verify_integrity=True)
    print()
    
    savename = f'./data/Elo_{year}_week{wk}.csv'
    print(f"Saving to {savename}")
    savedf.to_csv(savename, index=False)
    

if __name__ == '__main__':
    
    args = parser.parse_args()
    
    YEAR = args.year
    
    if args.week is None:
        week = input("Which week just finished (1-18)? ")
    else:
        week = args.week
        
    # Check if 'week' is actually a range of weeks
    if '-' in week:
            start, end = [int(i) for i in week.split('-')]
            weeks = list(range(start, end))
    else:
        assert week.isnumeric(), f"Invalid input: '{week}'"
        weeks = [int(week)]
    
    for WEEK in weeks:
        if yes_or_no(f"Do you need to record the scores for week {WEEK}?"):
            # TODO: utilize query_scores func. in api.py
            auto = yes_or_no("Would you like to use the API to update the scores automatically?")
            record_scores(WEEK, user_input=not auto)
        update_elos(WEEK) 