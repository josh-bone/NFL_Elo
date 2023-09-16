import numpy as np
import pandas as pd
K = 20

def initialize_elo(year, week=None):
    """Loads the current elo for every team

    Args:
        year (int): year of the season start. If None, all elo will be initialized to 1600.
        week (_type_, optional): Current week. Defaults to None. If None, we assume this is week 1.
    """       
    
    dic = {}
    
    if year is None:
        fname = './data/Elo_2022.csv'
        print(f"Reading {fname}")
        df = pd.read_csv(fname)
        for ind, row in df.iterrows():
            dic[row['Team']] = 1600
    else:
        if week is None or week==1:
            fname = f'./data/Elo_{year - 1}.csv'
        else:
            fname = f'./data/Elo_{year}_week{week - 1}.csv'
            
        print(f"Reading {fname}")
        df = pd.read_csv(fname)
        
        for ind, row in df.iterrows():
            dic[row['Team']] = row['Elo']
        
    return(dic)

def prob_to_odds(prob):
    """Converts from decimal probability (e.g. 0.75) to American betting odds (e.g. -300)

    Args:
        prob (float): Decimal probability
    """    
    if prob > .5:
        odds = - 100 / ((1 / prob) - 1)
    elif prob < .5:
        odds = ((1/prob) * 100) - 100
    else:
        odds = 100
        
    return(int(round(odds)))  # cast it to an integer

def prob_winning(A, B):
    """Returns the probability of Team A winning
    
    Reference: https://www.cantorsparadise.com/the-mathematics-of-elo-ratings-b6bfc9ca1dba

    Args:
        A (float): Elo of Team A
        B (float): Elo of Team B
    """    
    
    diff = A - B
    
    return( 1/ (10 ** (-diff/400) + 1 ))

def game_res(A, B):
    """Simple helper function to return the game result encoded as (1, 0, 0.5)

    Args:
        A (_type_): Points scored by team A
        B (_type_): Points scored by team B
    Returns:
        float: 1 if team A won, 0 if team B won, 0.5 if the game was a tie
    """    
    
    if A > B:
        return 1.0
    elif A < B:
        return 0.0
    else:
        return 0.5

def mov_mult(elo_A, elo_B, points_A, points_B):
    """Margin-of-victory multiplier
    
    It's OK to interchange A and B here

    Args:
        elo_A (_type_): Pre-game elo of team A
        elo_B (_type_): Pre-game elo of team B
        points_A (_type_): Points scored by team A
        points_B (_type_): Points scored by team B
    """    
    
    # NOTE: These differences are absolute value!!!
    point_diff = abs(points_A - points_B)
    elo_diff = abs(elo_A - elo_B)
    
    return( np.log(point_diff + 1)*(2.2 / (elo_diff * .001 + 2.2)) )

def update(elo_A, elo_B, points_A, points_B):
    """This function computes the new Elo for two teams

    Args:
        elo_A (_type_): Pre-game elo of team A
        elo_B (_type_): Pre-game elo of team B
        points_A (_type_): Points scored by team A
        points_B (_type_): Points scored by team B
    """    
    # assert type(points_A) == int and type(points_B) == int, f"Score needs to be integer! Instead points_A is {type(points_A)} and points_B is {type(points_B)}"
    # assert type(elo_A) in [float, int] and type(elo_B) in [float, int], f"Elo needs to be a number! Instead elo_A is {type(elo_A)} and elo_B is {type(elo_B)}"

    prob = prob_winning(elo_A, elo_B)
    mult = mov_mult(elo_A, elo_B, points_A, points_B)  # Margin-of-victory multiplier
    result = game_res(points_A, points_B)
    shift = (K * mult) * (result - prob)
    
    return(elo_A + shift, elo_B - shift)