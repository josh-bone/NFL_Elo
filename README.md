raw_user_forecasts.csv a dataset of user predictions for the 2022-23 season from fivethirtyeight's "[Elo Game](https://github.com/fivethirtyeight/nfl-elo-game)." 

"archive" is pulled from [this](https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data) kaggle dataset. It contains historical betting info.


## Elo Info

This system is based of the [elo system used by FiveThirtyEight](https://fivethirtyeight.com/methodology/how-our-nfl-predictions-work/). Elo is a score assigned to each team that represents their team-strength. It is derived from that team's performance in a closed pool of zero-sum games. 

Using elo, you can calculate the odds of team A winning a given game as:

\begin{equation*}
Pr(A) = \frac{1}{10^{\frac{-Elo Diff}{400}} + 1}
\end{equation*}


Here are the main features that go into updating elo scores in this system:

# The K-factor

This is a parameter that controls how quickly elo updates according to recent games. A high K-factor indicates that 

# The forecast delta 

This is how different the outcome of the game is from what the Elo system predicted.

# Margin-of-victory multiplier

\begin{equation*}
Mov Multiplier = \ln{(Winner Point Diff+1)} \times \frac{2.2}{Winner Elo Diff \times 0.001 + 2.2}
\end{equation*}

