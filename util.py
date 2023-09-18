import pickle as pkl
import os
import math

def yes_or_no(prompt):
    """Helper function for accepting command line input (CLI).

    Args:
        prompt (str): The string to be displayed to the user.

    Returns:
        _type_: _description_
    """    
    valid = {"y":True, "yes":True, "n":False, "no":False}
    
    if "y/n" not in prompt:
        prompt += " [y/n]\t"
    
    yn = input(prompt).casefold()
    assert yn in valid, "Did not recognize input"
    
    return valid[yn]

def validate_ratings(elo, ortg, drtg):
    for team in elo:
        assert math.isclose(elo[team], ortg[team] + drtg[team], rel_tol=1e-4), f"There is a mismatch between elo and off/def ratings for {team}!\n({ortg[team]:.1f} + {drtg[team]:.1f}!={elo[team]:.1f})."

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
