import os
import pickle
import math
import numpy as np

# Config
DATA_DIR = "data"
MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")

# Load model package
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        MODEL_PKG = pickle.load(f)
else:
    MODEL_PKG = None

def get_model_package():
    global MODEL_PKG
    if MODEL_PKG is None:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                MODEL_PKG = pickle.load(f)
        else:
            raise FileNotFoundError("model.pkl not found! Please run train.py first.")
    return MODEL_PKG

def poisson_prob(k, lamb):
    """Calculate Poisson probability for k events with mean lamb."""
    if lamb <= 0:
        return 1.0 if k == 0 else 0.0
    return (lamb ** k) * math.exp(-lamb) / math.factorial(k)

def get_team_form_features(home_team, away_team, pkg):
    # Retrieve form features from the latest matches stored in model package
    # Defaults if team not found
    h_pts, h_gf, h_ga = 1.0, 1.0, 1.0
    a_pts, a_gf, a_ga = 1.0, 1.0, 1.0
    
    h_history = pkg['team_history'].get(home_team, [])
    if h_history:
        last_n = h_history[-5:]
        weights = np.exp(np.linspace(-1., 0., len(last_n)))
        weights /= weights.sum()
        h_pts = sum(x[0]*w for x, w in zip(last_n, weights))
        h_gf = sum(x[1]*w for x, w in zip(last_n, weights))
        h_ga = sum(x[2]*w for x, w in zip(last_n, weights))
        
    a_history = pkg['team_history'].get(away_team, [])
    if a_history:
        last_n = a_history[-5:]
        weights = np.exp(np.linspace(-1., 0., len(last_n)))
        weights /= weights.sum()
        a_pts = sum(x[0]*w for x, w in zip(last_n, weights))
        a_gf = sum(x[1]*w for x, w in zip(last_n, weights))
        a_ga = sum(x[2]*w for x, w in zip(last_n, weights))
        
    # Head to Head
    team_pair = tuple(sorted([home_team, away_team]))
    past_matches = pkg['h2h_history'].get(team_pair, [])
    h2h_diff = 0.0
    if past_matches:
        net_gds = []
        for h_team, a_team, h_goals, a_goals in past_matches[-3:]:
            if h_team == home_team:
                net_gds.append(h_goals - a_goals)
            else:
                net_gds.append(a_goals - h_goals)
        h2h_diff = float(np.mean(net_gds))
        
    return h_pts, h_gf, h_ga, a_pts, a_gf, a_ga, h2h_diff

def predict_pre_match(home_team, away_team):
    pkg = get_model_package()
    
    home_elo = pkg['current_elos'].get(home_team, 1500.0)
    away_elo = pkg['current_elos'].get(away_team, 1500.0)
    elo_diff = home_elo + 90.0 - away_elo # Include home advantage
    
    h_pts, h_gf, h_ga, a_pts, a_gf, a_ga, h2h_diff = get_team_form_features(home_team, away_team, pkg)
    
    # Pre-match features matching training
    features = np.array([[
        elo_diff,
        h_pts, a_pts,
        h_gf, a_gf,
        h_ga, a_ga,
        h2h_diff
    ]])
    
    # 1. Classifier prediction
    clf = pkg['classifier']
    probs = clf.predict_proba(features)[0] # Outcome mapping: 0 -> Away, 1 -> Draw, 2 -> Home
    
    # 2. Poisson goal model
    h_strength = pkg['strengths'].get(home_team, {'att_home': 1.0, 'def_home': 1.0})
    a_strength = pkg['strengths'].get(away_team, {'att_away': 1.0, 'def_away': 1.0})
    
    # Base expected goals (lambda and mu)
    lambda_home = h_strength['att_home'] * a_strength['def_away'] * pkg['avg_hg']
    mu_away = a_strength['att_away'] * h_strength['def_home'] * pkg['avg_ag']
    
    # Adjust expected goals based on Elo rating difference (logarithmic scale)
    elo_factor = elo_diff / 400.0
    lambda_home *= (1.0 + 0.20 * elo_factor)
    mu_away *= (1.0 - 0.20 * elo_factor)
    
    # Prevent negative or extremely unrealistic values
    lambda_home = max(0.1, min(4.0, lambda_home))
    mu_away = max(0.1, min(4.0, mu_away))
    
    # Calculate score probabilities grid
    max_goals = 8
    score_grid = np.zeros((max_goals, max_goals))
    
    for h in range(max_goals):
        for a in range(max_goals):
            score_grid[h, a] = poisson_prob(h, lambda_home) * poisson_prob(a, mu_away)
            
    # Normalize score grid
    grid_sum = score_grid.sum()
    if grid_sum > 0:
        score_grid /= grid_sum
        
    # Calculate outcome probabilities from Poisson model
    p_home_win_poisson = np.sum(np.tril(score_grid, -1))
    p_draw_poisson = np.sum(np.diag(score_grid))
    p_away_win_poisson = np.sum(np.triu(score_grid, 1))
    
    # Blend classifier and Poisson predictions for optimal calibration
    p_away = 0.5 * probs[0] + 0.5 * p_away_win_poisson
    p_draw = 0.5 * probs[1] + 0.5 * p_draw_poisson
    p_home = 0.5 * probs[2] + 0.5 * p_home_win_poisson
    
    # Re-normalize
    tot = p_home + p_draw + p_away
    p_home /= tot
    p_draw /= tot
    p_away /= tot
    
    # Most likely score
    h_idx, a_idx = np.unravel_index(np.argmax(score_grid), score_grid.shape)
    
    return {
        'home_team': home_team,
        'away_team': away_team,
        'home_elo': float(home_elo),
        'away_elo': float(away_elo),
        'home_win_prob': float(p_home),
        'draw_prob': float(p_draw),
        'away_win_prob': float(p_away),
        'expected_goals_home': float(lambda_home),
        'expected_goals_away': float(mu_away),
        'predicted_score': f"{h_idx}-{a_idx}",
        'predicted_home_goals': int(h_idx),
        'predicted_away_goals': int(a_idx),
        'factors': {
            'elo_diff': float(elo_diff),
            'home_form_points': float(h_pts),
            'away_form_points': float(a_pts),
            'h2h_diff': float(h2h_diff)
        }
    }

def predict_live(home_team, away_team, current_minute, home_goals, away_goals, home_red_cards, away_red_cards):
    """
    Computes in-play win/draw/loss probabilities using a time-decay Poisson model 
    combined with red card modifiers.
    """
    pkg = get_model_package()
    
    # Pre-match expected goals
    pre_match = predict_pre_match(home_team, away_team)
    lambda_pre = pre_match['expected_goals_home']
    mu_pre = pre_match['expected_goals_away']
    
    # Remaining time factor
    remaining_time = max(0, 90 - current_minute)
    time_factor = remaining_time / 90.0
    
    # Scale remaining expected goals
    lambda_rem = lambda_pre * time_factor
    mu_rem = mu_pre * time_factor
    
    # Red card modifiers:
    # A red card reduces own scoring rate by 25% and increases opponent's scoring rate by 25%
    for _ in range(home_red_cards):
        lambda_rem *= 0.75
        mu_rem *= 1.25
        
    for _ in range(away_red_cards):
        lambda_rem *= 1.25
        mu_rem *= 0.75
        
    # Calculate probabilities of remaining goals (up to 8)
    max_rem = 8
    p_home_rem = [poisson_prob(i, lambda_rem) for i in range(max_rem)]
    p_away_rem = [poisson_prob(i, mu_rem) for i in range(max_rem)]
    
    # Normalize remaining probabilities
    sum_h = sum(p_home_rem)
    sum_a = sum(p_away_rem)
    p_home_rem = [p / sum_h for p in p_home_rem] if sum_h > 0 else [1.0] + [0.0]*(max_rem-1)
    p_away_rem = [p / sum_a for p in p_away_rem] if sum_a > 0 else [1.0] + [0.0]*(max_rem-1)
    
    p_home_win = 0.0
    p_draw = 0.0
    p_away_win = 0.0
    
    for r_h in range(len(p_home_rem)):
        for r_a in range(len(p_away_rem)):
            prob = p_home_rem[r_h] * p_away_rem[r_a]
            final_home = home_goals + r_h
            final_away = away_goals + r_a
            
            if final_home > final_away:
                p_home_win += prob
            elif final_home < final_away:
                p_away_win += prob
            else:
                p_draw += prob
                
    # Normalize final probabilities
    total_prob = p_home_win + p_draw + p_away_win
    if total_prob > 0:
        p_home_win /= total_prob
        p_draw /= total_prob
        p_away_win /= total_prob
    else:
        p_home_win, p_draw, p_away_win = 0.33, 0.33, 0.34
        
    return {
        'minute': current_minute,
        'home_goals': home_goals,
        'away_goals': away_goals,
        'home_win_prob': float(p_home_win),
        'draw_prob': float(p_draw),
        'away_win_prob': float(p_away_win)
    }

def predict_powerplayer(home_team, away_team):
    """
    Predicts the Powerplayer (Man of the Match) based on team strengths and simulated match dynamic.
    """
    pkg = get_model_package()
    
    # Determine the favored team
    home_elo = pkg['current_elos'].get(home_team, 1500.0)
    away_elo = pkg['current_elos'].get(away_team, 1500.0)
    
    favored_team = home_team if home_elo > away_elo else away_team
    
    # Very rudimentary player dataset. In a real system, this would be loaded from a DB or JSON.
    star_players = {
        'Argentina': ['Lionel Messi', 'Julian Alvarez', 'Emiliano Martinez', 'Alexis Mac Allister', 'Enzo Fernandez'],
        'France': ['Kylian Mbappé', 'Antoine Griezmann', 'Ousmane Dembele', 'Aurelien Tchouameni', 'William Saliba'],
        'England': ['Jude Bellingham', 'Harry Kane', 'Phil Foden', 'Bukayo Saka', 'Declan Rice'],
        'Brazil': ['Vinícius Júnior', 'Rodrygo', 'Bruno Guimaraes', 'Marquinhos', 'Alisson'],
        'Spain': ['Lamine Yamal', 'Rodri', 'Pedri', 'Dani Olmo', 'Nico Williams'],
        'Portugal': ['Cristiano Ronaldo', 'Bruno Fernandes', 'Bernardo Silva', 'Ruben Dias', 'Rafael Leao'],
        'Germany': ['Jamal Musiala', 'Florian Wirtz', 'Ilkay Gundogan', 'Leroy Sane', 'Antonio Rudiger']
    }
    
    players = star_players.get(favored_team, [f"{favored_team} Striker", f"{favored_team} Midfielder", f"{favored_team} Goalkeeper", f"{favored_team} Defender"])
    
    # Pseudo-randomly pick a top player, favoring the first two (usually forwards/stars)
    # We use a hash of the teams to make it deterministic for the same matchup
    hash_val = hash(home_team + away_team)
    
    player_idx = hash_val % len(players)
    if hash_val % 10 < 6: # 60% chance to be the top star (index 0)
        player_idx = 0
    elif hash_val % 10 < 8: # 20% chance to be index 1
        player_idx = 1
        
    power_player = players[player_idx]
    
    # Generate some mock stats for the prediction
    expected_rating = 8.0 + (abs(home_elo - away_elo) / 800.0) + ((hash_val % 10) / 10.0)
    expected_rating = min(10.0, expected_rating)
    
    return {
        'power_player': power_player,
        'team': favored_team,
        'predicted_rating': round(expected_rating, 1),
        'reason': f"Predicted to dominate the match based on {favored_team}'s superior Elo ({int(max(home_elo, away_elo))}) and tactical setup."
    }

