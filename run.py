import argparse

from weekly_update import record_scores, update_elos
from predict_week import query_schedule
from util import yes_or_no

parser = argparse.ArgumentParser(
                    prog='Predict Week',
                    description='This script accepts a schedule as CLI-input, and predicts the outcome for the upcoming games.')
parser.add_argument('-w', '--week', type=int)
parser.add_argument('-y', '--year', type=int, default=2023, help="The last *completed* week of games")
parser.add_argument('-a', '--api', action='store_true', help="Call this if you want to use the API instead of command line input")


if __name__ == '__main__':
    
    args = parser.parse_args()
    if args.week is None:
        WEEK = int(input("What week are you making picks for (1-18)?\t"))
    else:
        WEEK = args.week
    
    if args.api:
        user_input = False
    else:
        user_input = yes_or_no("Do you want to enter the data manually?")
    
    # Update
    record_scores(WEEK, year=args.year, user_input=user_input)
    update_elos(WEEK, year=args.year)
        
    # Predict
    query_schedule(WEEK + 1, year=args.year, user_input=user_input)