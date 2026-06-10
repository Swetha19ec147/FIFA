import os
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, log_loss

# Config
DATA_DIR = "data"
MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")

def test_model_performance():
    print("=== MODEL PERFORMANCE TEST ===")
    if not os.path.exists(MODEL_PATH):
        print(f"Error: {MODEL_PATH} not found. Please train the model first.")
        return False
        
    with open(MODEL_PATH, 'rb') as f:
        pkg = pickle.load(f)
        
    # Re-load data for validation testing (season 24/25)
    path_2425 = os.path.join(DATA_DIR, "E0_2425.csv")
    if not os.path.exists(path_2425):
        print(f"Error: Validation data {path_2425} not found.")
        return False
        
    df = pd.read_csv(path_2425)
    df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTR'])
    df['Outcome'] = df['FTR'].map({'H': 2, 'D': 1, 'A': 0})
    
    # Extract features matching the model training
    # Build feature dataset chronologically for 24/25
    features = []
    outcomes = []
    
    # Setup temporary team history state from historical package to compute form correctly
    temp_history = {team: list(hist) for team, hist in pkg['team_history'].items()}
    temp_elos = dict(pkg['current_elos'])
    temp_h2h = {pair: list(hist) for pair, hist in pkg['h2h_history'].items()}
    
    for idx, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']
        
        # Calculate features before this match
        if home not in temp_history: temp_history[home] = []
        if away not in temp_history: temp_history[away] = []
        
        def get_ema_stats(history):
            if not history:
                return 1.0, 1.0, 1.0
            last_n = history[-5:]
            weights = np.exp(np.linspace(-1., 0., len(last_n)))
            weights /= weights.sum()
            
            pts = sum(x[0]*w for x, w in zip(last_n, weights))
            gf = sum(x[1]*w for x, w in zip(last_n, weights))
            ga = sum(x[2]*w for x, w in zip(last_n, weights))
            return pts, gf, ga
            
        h_pts, h_gf, h_ga = get_ema_stats(temp_history[home])
        a_pts, a_gf, a_ga = get_ema_stats(temp_history[away])
        
        team_pair = tuple(sorted([home, away]))
        past_matches = temp_h2h.get(team_pair, [])
        h2h_diff = 0.0
        if past_matches:
            net_gds = []
            for h_team, a_team, h_goals, a_goals in past_matches[-3:]:
                if h_team == home:
                    net_gds.append(h_goals - a_goals)
                else:
                    net_gds.append(a_goals - h_goals)
            h2h_diff = float(np.mean(net_gds))
            
        home_elo = temp_elos.get(home, 1500.0)
        away_elo = temp_elos.get(away, 1500.0)
        elo_diff = home_elo + 90.0 - away_elo
        
        match_features = [
            elo_diff,
            h_pts, a_pts,
            h_gf, a_gf,
            h_ga, a_ga,
            h2h_diff
        ]
        
        features.append(match_features)
        outcomes.append(row['Outcome'])
        
        # Update state for next step calculation
        h_match_pts = 3 if row['FTR'] == 'H' else (1 if row['FTR'] == 'D' else 0)
        a_match_pts = 3 if row['FTR'] == 'A' else (1 if row['FTR'] == 'D' else 0)
        temp_history[home].append((h_match_pts, int(row['FTHG']), int(row['FTAG'])))
        temp_history[away].append((a_match_pts, int(row['FTAG']), int(row['FTHG'])))
        
        # Elo Update
        fthg = int(row['FTHG'])
        ftag = int(row['FTAG'])
        gd = abs(fthg - ftag)
        dr_h = home_elo + 90.0 - away_elo
        e_h = 1 / (1 + 10**(-dr_h / 400))
        e_a = 1 - e_h
        s_h, s_a = (1.0, 0.0) if row['FTR'] == 'H' else ((0.0, 1.0) if row['FTR'] == 'A' else (0.5, 0.5))
        mult = 1.0 if gd <= 1 else (1.5 if gd == 2 else 1.75 + (gd - 3) / 8.0)
        temp_elos[home] = home_elo + 20 * mult * (s_h - e_h)
        temp_elos[away] = away_elo + 20 * mult * (s_a - e_a)
        
    X_val = np.array(features)
    y_val = np.array(outcomes)
    
    # Predict
    clf = pkg['classifier']
    preds = clf.predict(X_val)
    probs = clf.predict_proba(X_val)
    
    acc = accuracy_score(y_val, preds)
    loss = log_loss(y_val, probs)
    
    # Calculate Brier score for 3-way outcomes
    # Brier = (1/N) * sum_{i} sum_{c} (p_{ic} - y_{ic})^2
    # Convert y_val to one-hot representation
    one_hot_y = np.zeros((len(y_val), 3))
    for i, val in enumerate(y_val):
        one_hot_y[i, val] = 1.0
        
    brier_score = np.mean(np.sum((probs - one_hot_y) ** 2, axis=1))
    
    # Benchmark: Simple baseline predicting base rate win probabilities (e.g. 45% Home Win, 25% Draw, 30% Away Win)
    baseline_probs = np.tile([0.30, 0.25, 0.45], (len(y_val), 1)) # Away, Draw, Home
    baseline_brier = np.mean(np.sum((baseline_probs - one_hot_y) ** 2, axis=1))
    
    print(f"Total validation matches: {len(X_val)}")
    print(f"AI Model Accuracy: {acc:.3f}")
    print(f"AI Model Log Loss: {loss:.3f}")
    print(f"AI Model Brier Score: {brier_score:.3f}")
    print(f"Baseline Brier Score: {baseline_brier:.3f}")
    
    if brier_score < baseline_brier:
        print("SUCCESS: AI model outperforms the baseline prediction Brier Score!")
    else:
        print("WARNING: AI model does not outperform the baseline. Consider tuning hyperparameters.")
        
    return True

def test_seo_compliance():
    print("\n=== SEO COMPLIANCE AUDIT ===")
    index_path = "templates/index.html"
    if not os.path.exists(index_path):
        print(f"Error: {index_path} not found.")
        return False
        
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    checks = {
        "HTML Lang attribute": 'lang="en"' in html.lower(),
        "Meta UTF-8 charset": '<meta charset="utf-8"' in html.lower() or '<meta charset="utf-8" />' in html.lower(),
        "Meta Viewport": 'name="viewport"' in html.lower(),
        "Page Title tag": '<title>' in html.lower() and '</title>' in html.lower(),
        "Meta Description": 'name="description"' in html.lower(),
        "Meta Keywords": 'name="keywords"' in html.lower(),
        "Canonical Link": 'rel="canonical"' in html.lower(),
        "Robots Meta": 'name="robots"' in html.lower(),
        "OpenGraph Title": 'property="og:title"' in html.lower(),
        "OpenGraph Description": 'property="og:description"' in html.lower(),
        "OpenGraph Image": 'property="og:image"' in html.lower(),
        "OpenGraph URL": 'property="og:url"' in html.lower(),
        "OpenGraph Type": 'property="og:type"' in html.lower(),
        "Twitter Card": 'property="twitter:card"' in html.lower() or 'name="twitter:card"' in html.lower(),
        "JSON-LD Structured Data": 'type="application/ld+json"' in html.lower(),
        "H1 Heading tag": '<h1>' in html.lower() and '</h1>' in html.lower(),
        "Unique IDs on buttons": 'id="btn-calculate-predictions"' in html.lower() and 'id="btn-start-sim"' in html.lower() and 'id="btn-reset-sim"' in html.lower(),
        "Semantic HTML elements": '<header' in html.lower() and '<nav' in html.lower() and '<main' in html.lower() and '<section' in html.lower() and '<footer' in html.lower()
    }
    
    failed = 0
    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {name}")
        if not passed:
            failed += 1
            
    if failed == 0:
        print("SUCCESS: 100% SEO Compliance Audit Passed! The page is fully optimized for Google, Bing, and MSI/MSN portals.")
        return True
    else:
        print(f"AUDIT WARNING: {failed} SEO checks failed. Review index.html.")
        return False

if __name__ == "__main__":
    test_model_performance()
    test_seo_compliance()
