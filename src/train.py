import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss

# Config
DATA_DIR = "data"
MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")
K_FACTOR = 20
HOME_ADVANTAGE = 90
FORM_WINDOW = 5

def load_data():
    seasons = ["1819", "1920", "2021", "2122", "2223", "2324", "2425"]
    dfs = []
    for s in seasons:
        path = os.path.join(DATA_DIR, f"E0_{s}.csv")
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTR'])
                df['Season'] = s
                # Handle dates safely
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce').fillna(
                    pd.to_datetime(df['Date'], format='%d/%m/%y', errors='coerce')
                )
                # Ensure goal columns are integer
                df['FTHG'] = df['FTHG'].astype(int)
                df['FTAG'] = df['FTAG'].astype(int)
                dfs.append(df)
            except Exception as e:
                print(f"Error reading {path}: {e}")
        else:
            print(f"Warning: Data for season {s} not found at {path}.")
    
    if not dfs:
        raise ValueError("No match data loaded! Please run download_data.py first.")
        
    all_df = pd.concat(dfs, ignore_index=True)
    all_df = all_df.sort_values(by=['Date']).reset_index(drop=True)
    return all_df

def compute_elo_ratings(df):
    teams = set(df['HomeTeam'].unique()).union(set(df['AwayTeam'].unique()))
    current_elos = {team: 1500.0 for team in teams}
    
    # Track Elo history for each team: list of (date, elo)
    elo_history = {team: [(pd.Timestamp('2018-08-01'), 1500.0)] for team in teams}
    
    home_elos = []
    away_elos = []
    
    for idx, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']
        result = row['FTR']
        date = row['Date']
        gd = abs(row['FTHG'] - row['FTAG'])
        
        r_h = current_elos[home]
        r_a = current_elos[away]
        
        home_elos.append(r_h)
        away_elos.append(r_a)
        
        # Expected scores
        dr_h = r_h + HOME_ADVANTAGE - r_a
        e_h = 1 / (1 + 10**(-dr_h / 400))
        e_a = 1 - e_h
        
        # Actual result score
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
        new_r_h = r_h + K_FACTOR * mult * (s_h - e_h)
        new_r_a = r_a + K_FACTOR * mult * (s_a - e_a)
        
        current_elos[home] = new_r_h
        current_elos[away] = new_r_a
        
        elo_history[home].append((date, new_r_h))
        elo_history[away].append((date, new_r_a))
        
    df['HomeElo'] = home_elos
    df['AwayElo'] = away_elos
    df['EloDiff'] = df['HomeElo'] + HOME_ADVANTAGE - df['AwayElo']
    
    return current_elos, elo_history

def compute_rolling_features(df):
    # Store team games chronologically
    team_history = {}
    
    home_form_pts = []
    away_form_pts = []
    home_form_gf = []
    away_form_gf = []
    home_form_ga = []
    away_form_ga = []
    
    for idx, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']
        
        # Initialize team history if not present
        # Store as: (points, goals_scored, goals_conceded)
        if home not in team_history:
            team_history[home] = []
        if away not in team_history:
            team_history[away] = []
            
        # Calculate EMA stats BEFORE this match
        def get_ema_stats(history):
            if not history:
                return 1.0, 1.0, 1.0  # Baselines
            last_n = history[-FORM_WINDOW:]
            weights = np.exp(np.linspace(-1., 0., len(last_n)))
            weights /= weights.sum()
            
            pts = sum(x[0]*w for x, w in zip(last_n, weights))
            gf = sum(x[1]*w for x, w in zip(last_n, weights))
            ga = sum(x[2]*w for x, w in zip(last_n, weights))
            return pts, gf, ga
            
        h_pts, h_gf, h_ga = get_ema_stats(team_history[home])
        a_pts, a_gf, a_ga = get_ema_stats(team_history[away])
        
        home_form_pts.append(h_pts)
        away_form_pts.append(a_pts)
        home_form_gf.append(h_gf)
        away_form_gf.append(a_gf)
        home_form_ga.append(h_ga)
        away_form_ga.append(a_ga)
        
        # Append this match results to history
        h_match_pts = 3 if row['FTR'] == 'H' else (1 if row['FTR'] == 'D' else 0)
        a_match_pts = 3 if row['FTR'] == 'A' else (1 if row['FTR'] == 'D' else 0)
        
        team_history[home].append((h_match_pts, row['FTHG'], row['FTAG']))
        team_history[away].append((a_match_pts, row['FTAG'], row['FTHG']))
        
    df['HomeFormPoints'] = home_form_pts
    df['AwayFormPoints'] = away_form_pts
    df['HomeFormGF'] = home_form_gf
    df['AwayFormGF'] = away_form_gf
    df['HomeFormGA'] = home_form_ga
    df['AwayFormGA'] = away_form_ga
    
    return team_history

def compute_h2h_features(df):
    h2h_history = {}
    h2h_home_diff = []
    
    for idx, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']
        
        # Sort team pair name to always have a unique key
        team_pair = tuple(sorted([home, away]))
        
        if team_pair not in h2h_history:
            h2h_history[team_pair] = []
            
        # Get historical outcomes (from home's perspective relative to this match)
        past_matches = h2h_history[team_pair]
        if not past_matches:
            h2h_home_diff.append(0.0)
        else:
            # Calculate average net goal difference for home team in past matches
            net_gds = []
            for h_team, a_team, h_goals, a_goals in past_matches[-3:]: # Last 3 matchups
                if h_team == home:
                    net_gds.append(h_goals - a_goals)
                else:
                    net_gds.append(a_goals - h_goals)
            h2h_home_diff.append(np.mean(net_gds))
            
        # Save this match
        h2h_history[team_pair].append((home, away, row['FTHG'], row['FTAG']))
        
    df['H2HDiff'] = h2h_home_diff
    return h2h_history

def compute_team_strengths(df):
    # Focus on the last 2 seasons (2324 & 2425) for current strength calculations
    recent_df = df[df['Season'].isin(["2324", "2425"])].copy()
    if recent_df.empty:
        recent_df = df.copy()
        
    # League wide averages
    avg_home_goals = recent_df['FTHG'].mean()
    avg_away_goals = recent_df['FTAG'].mean()
    
    teams = set(df['HomeTeam'].unique())
    strengths = {}
    
    for team in teams:
        home_games = recent_df[recent_df['HomeTeam'] == team]
        away_games = recent_df[recent_df['AwayTeam'] == team]
        
        # Attack strength (scored vs league average)
        if len(home_games) > 0:
            att_home = home_games['FTHG'].mean() / avg_home_goals
            def_home = home_games['FTAG'].mean() / avg_away_goals
        else:
            att_home, def_home = 1.0, 1.0
            
        if len(away_games) > 0:
            att_away = away_games['FTAG'].mean() / avg_away_goals
            def_away = away_games['FTHG'].mean() / avg_home_goals
        else:
            att_away, def_away = 1.0, 1.0
            
        # General stats (for simulation)
        # Average shots, corners, cards
        all_games = pd.concat([
            home_games.rename(columns={'HS': 'Shots', 'HC': 'Corners', 'HY': 'Yellow', 'HR': 'Red'}),
            away_games.rename(columns={'AS': 'Shots', 'AC': 'Corners', 'AY': 'Yellow', 'AR': 'Red'})
        ])
        
        strengths[team] = {
            'att_home': att_home,
            'def_home': def_home,
            'att_away': att_away,
            'def_away': def_away,
            'avg_shots': all_games['Shots'].mean() if not all_games.empty and 'Shots' in all_games else 12.0,
            'avg_corners': all_games['Corners'].mean() if not all_games.empty and 'Corners' in all_games else 5.0,
            'avg_yellow': all_games['Yellow'].mean() if not all_games.empty and 'Yellow' in all_games else 1.8,
            'avg_red': all_games['Red'].mean() if not all_games.empty and 'Red' in all_games else 0.1,
        }
        
    return strengths, avg_home_goals, avg_away_goals

def train_model():
    print("Loading data...")
    df = load_data()
    
    print("Calculating Elo ratings...")
    current_elos, elo_history = compute_elo_ratings(df)
    
    print("Calculating rolling form features...")
    team_history = compute_rolling_features(df)
    
    print("Calculating head-to-head features...")
    h2h_history = compute_h2h_features(df)
    
    print("Calculating Poisson team strengths...")
    strengths, avg_hg, avg_ag = compute_team_strengths(df)
    
    # Feature columns for ML
    features = [
        'EloDiff', 
        'HomeFormPoints', 'AwayFormPoints',
        'HomeFormGF', 'AwayFormGF',
        'HomeFormGA', 'AwayFormGA',
        'H2HDiff'
    ]
    
    # Let's map outcome: H -> 2, D -> 1, A -> 0
    df['Outcome'] = df['FTR'].map({'H': 2, 'D': 1, 'A': 0})
    
    # Drop rows with NaN features
    train_df = df.dropna(subset=features + ['Outcome']).copy()
    
    # Train / Test split (Train on everything before season 2425, validate on 2425)
    train_split = train_df[train_df['Season'] != '2425']
    val_split = train_df[train_df['Season'] == '2425']
    
    if val_split.empty:
        # If 2425 doesn't exist yet, split by last 20%
        split_idx = int(len(train_df) * 0.8)
        train_split = train_df.iloc[:split_idx]
        val_split = train_df.iloc[split_idx:]
        
    X_train = train_split[features]
    y_train = train_split['Outcome']
    X_val = val_split[features]
    y_val = val_split['Outcome']
    
    print(f"Training set size: {len(X_train)} matches")
    print(f"Validation set size: {len(X_val)} matches")
    
    # Train Classifier
    clf = GradientBoostingClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    train_preds = clf.predict(X_train)
    val_preds = clf.predict(X_val)
    val_probs = clf.predict_proba(X_val)
    
    print(f"Train Accuracy: {accuracy_score(y_train, train_preds):.3f}")
    print(f"Validation Accuracy: {accuracy_score(y_val, val_preds):.3f}")
    print(f"Validation Log Loss: {log_loss(y_val, val_probs):.3f}")
    
    # Re-train on all data for production use
    print("Retraining classifier on full dataset...")
    clf_final = GradientBoostingClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42)
    clf_final.fit(train_df[features], train_df['Outcome'])
    
    # Save the model package
    model_package = {
        'classifier': clf_final,
        'features': features,
        'current_elos': current_elos,
        'elo_history': elo_history,
        'strengths': strengths,
        'avg_hg': avg_hg,
        'avg_ag': avg_ag,
        'team_history': team_history,
        'h2h_history': h2h_history,
        # Save a list of latest match entries to get current form quickly
        'latest_df': df.tail(150).to_dict(orient='records')
    }
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_package, f)
        
    print(f"Model successfully saved to {MODEL_PATH}!")

if __name__ == "__main__":
    train_model()
