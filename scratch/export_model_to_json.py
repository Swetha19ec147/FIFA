import os
import sys
import pickle
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

MODEL_PATH = os.path.join(BASE_DIR, "data", "model.pkl")
CSV_PATH = os.path.join(BASE_DIR, "data", "E0_2425.csv")
OUTPUT_JS = os.path.join(BASE_DIR, "static", "js", "model_data.js")
OUTPUT_JS_DEPLOY = os.path.join(BASE_DIR, "netlify_deploy", "static", "js", "model_data.js")

def export_data():
    if not os.path.exists(MODEL_PATH):
        print("model.pkl not found!")
        return
        
    with open(MODEL_PATH, 'rb') as f:
        pkg = pickle.load(f)
        
    # Format current elos
    current_elos = pkg['current_elos']
    
    # Format Elo history (serialize timestamps to string YYYY-MM-DD)
    elo_history = {}
    for team, history in pkg['elo_history'].items():
        elo_history[team] = []
        for date, val in history:
            date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            elo_history[team].append({'date': date_str, 'elo': float(val)})
            
    # Format team history
    team_history = pkg['team_history']
    
    # Format H2H history (keys are tuples, need to convert to string e.g. "teamA__teamB" for JSON)
    h2h_history = {}
    for pair, matches in pkg['h2h_history'].items():
        key = f"{pair[0]}__{pair[1]}"
        h2h_history[key] = []
        for home, away, hg, ag in matches:
            h2h_history[key].append({
                'home': home,
                'away': away,
                'home_goals': int(hg),
                'away_goals': int(ag)
            })
            
    # Format team strengths
    strengths = pkg['strengths']
    
    # Load completed matches for standings
    matches_list = []
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTR'])
        for idx, row in df.iterrows():
            date_str = row['Date'].strftime('%d/%m/%Y') if hasattr(row['Date'], 'strftime') else str(row['Date'])
            matches_list.append({
                'date': date_str,
                'home_team': row['HomeTeam'],
                'away_team': row['AwayTeam'],
                'home_goals': int(row['FTHG']),
                'away_goals': int(row['FTAG']),
                'result': row['FTR']
            })
            
    # Load manual data dynamically
    from app import app, get_manual
    with app.test_request_context():
        manual_payload = json.loads(get_manual().data.decode('utf-8'))['manual']
        
    # Serialize Random Forest Classifier trees
    clf = pkg['classifier']
    forest = []
    for estimator in clf.estimators_:
        tree = estimator.tree_
        nodes = []
        for i in range(tree.node_count):
            left = int(tree.children_left[i])
            right = int(tree.children_right[i])
            feature = int(tree.feature[i])
            threshold = float(tree.threshold[i])
            val = [float(x) for x in tree.value[i][0]]
            nodes.append({
                'left': left,
                'right': right,
                'feature': feature,
                'threshold': threshold,
                'value': val
            })
        forest.append(nodes)
        
    model_data = {
        'current_elos': current_elos,
        'elo_history': elo_history,
        'team_history': team_history,
        'h2h_history': h2h_history,
        'strengths': strengths,
        'avg_hg': float(pkg['avg_hg']),
        'avg_ag': float(pkg['avg_ag']),
        'matches_2425': matches_list,
        'manual': manual_payload,
        'forest': forest
    }
    
    # Write as a JavaScript variable assignment
    js_content = f"// Automatically generated database from model.pkl and matches CSV\nconst MODEL_DATA = {json.dumps(model_data, indent=2)};\n"
    
    # Write to static folder
    os.makedirs(os.path.dirname(OUTPUT_JS), exist_ok=True)
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Successfully exported data to {OUTPUT_JS} ({len(js_content)} bytes).")
    
    # Write to netlify_deploy folder
    os.makedirs(os.path.dirname(OUTPUT_JS_DEPLOY), exist_ok=True)
    with open(OUTPUT_JS_DEPLOY, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Successfully exported data to {OUTPUT_JS_DEPLOY} ({len(js_content)} bytes).")

if __name__ == "__main__":
    export_data()
