import pickle as pkl
import os

def validate_ratings(elo, ortg, drtg):
    for team in elo:
        assert elo[team] == ortg[team] + drtg[team], "There is a mismatch between elo and off/def ratings! Check the data."

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
