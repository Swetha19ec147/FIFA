import urllib.request
import pandas as pd
import numpy as np
import io
import os

seasons = ["1819", "1920", "2021", "2122", "2223", "2324"]
data_frames = []

for season in seasons:
    url = f"https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
    print(f"Downloading season {season}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read()
        df = pd.read_csv(io.BytesIO(html))
        # Drop columns that are entirely NaN or matches that are not played
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTR'])
        df['Season'] = season
        # Standardize dates
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce').fillna(
            pd.to_datetime(df['Date'], format='%d/%m/%y', errors='coerce')
        )
        data_frames.append(df)
        print(f"Successfully loaded {len(df)} matches.")
    except Exception as e:
        print(f"Error loading {season}: {e}")

# Combine and sort chronologically
all_matches = pd.concat(data_frames, ignore_index=True)
all_matches = all_matches.sort_values(by=['Date']).reset_index(drop=True)
print(f"Total matches loaded: {len(all_matches)}")

# Elo rating parameters
K = 20
HOME_ADVANTAGE = 90
elo_ratings = {}

# Initialize all teams at 1500
teams = set(all_matches['HomeTeam'].unique()).union(set(all_matches['AwayTeam'].unique()))
for team in teams:
    elo_ratings[team] = 1500.0

elo_history_home = []
elo_history_away = []

for idx, row in all_matches.iterrows():
    home = row['HomeTeam']
    away = row['AwayTeam']
    result = row['FTR'] # H, D, A
    fthg = int(row['FTHG'])
    ftag = int(row['FTAG'])
    gd = abs(fthg - ftag)
    
    # Store pre-match Elos
    r_h = elo_ratings[home]
    r_a = elo_ratings[away]
    elo_history_home.append(r_h)
    elo_history_away.append(r_a)
    
    # Expected scores
    # Home has home advantage
    dr_h = r_h + HOME_ADVANTAGE - r_a
    e_h = 1 / (1 + 10**(-dr_h / 400))
    
    dr_a = r_a - (r_h + HOME_ADVANTAGE)
    e_a = 1 / (1 + 10**(-dr_a / 400))
    
    # Actual result
    if result == 'H':
        s_h, s_a = 1.0, 0.0
    elif result == 'A':
        s_h, s_a = 0.0, 1.0
    else:
        s_h, s_a = 0.5, 0.5
        
    # Goal difference multiplier
    if gd <= 1:
        mult = 1.0
    elif gd == 2:
        mult = 1.5
    else:
        mult = 1.75 + (gd - 3) / 8.0
        
    # Update Elos
    new_r_h = r_h + K * mult * (s_h - e_h)
    new_r_a = r_a + K * mult * (s_a - e_a)
    
    elo_ratings[home] = new_r_h
    elo_ratings[away] = new_r_a

all_matches['HomeElo'] = elo_history_home
all_matches['AwayElo'] = elo_history_away
all_matches['EloDiff'] = all_matches['HomeElo'] + HOME_ADVANTAGE - all_matches['AwayElo']

# Check correlation between EloDiff and Result
all_matches['HomeWin'] = (all_matches['FTR'] == 'H').astype(int)
all_matches['AwayWin'] = (all_matches['FTR'] == 'A').astype(int)
all_matches['Draw'] = (all_matches['FTR'] == 'D').astype(int)

print("\nElo Prediction Stats:")
print("Correlation of EloDiff with HomeWin:", all_matches['EloDiff'].corr(all_matches['HomeWin']))
print("Correlation of EloDiff with AwayWin:", (-all_matches['EloDiff']).corr(all_matches['AwayWin']))

# Group by EloDiff bins and calculate win rates
all_matches['EloDiffBin'] = pd.qcut(all_matches['EloDiff'], 5)
print("\nWin rates by Elo difference bins:")
print(all_matches.groupby('EloDiffBin', observed=False)['HomeWin'].mean())

# Print top 10 teams by current Elo
print("\nTop 10 Teams by Current Elo:")
sorted_teams = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
for i, (team, elo) in enumerate(sorted_teams[:10]):
    print(f"{i+1}. {team}: {elo:.1f}")
