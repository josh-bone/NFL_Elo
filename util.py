import pickle as pkl
import os
import math

def query_team(prompt, alias_filename='alias.pkl'):
    """queries the user to input a VALID NFL team name

    Args:
        prompt (str): str to, output to the CLI in order to prompt user input
        alias (dict): (nickname, teamname) key-value pairs

    Returns:
        teamname (str): The capitalized and corrected name of the NFL team (e.g. Patriots)
    """    
    
    """
    The 'alias' variable is a dictionary that contains nicknames/aliases as keys and true team names as values. 
    All strings, and all uppercase.
    """
    alias = load_pkl(alias_filename)
    
    teamname = input(prompt).capitalize()
    if teamname.lower() == 'q': return False
    
    while teamname.isnumeric():
        print(f"It seems like you accidentally entered a score...")
        teamname = input(prompt).capitalize()

    while teamname not in alias.keys():
        print(f"I didn't recognize the team {teamname}...")
        if yes_or_no(f"Would you like to save {teamname} as an alias for an NFL team?"):
            true_team = input(f"For which team is {teamname} an alias? ").capitalize()
            
            if true_team in alias.values():  # If we recognize 'true_team'
                alias[teamname] = true_team.capitalize()  # save 'teamname' as an alias for 'true_team'
            
    teamname = alias[teamname]
    
    # In case we made changes (added nicknames/aliases), save this dictionary to file
    save_pkl(alias, alias_filename)
    
    return teamname

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
