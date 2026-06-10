import os
import sys
import pickle
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

MODEL_PATH = os.path.join(BASE_DIR, "data", "model.pkl")
OUTPUT_JS = os.path.join(BASE_DIR, "static", "js", "model_data.js")
OUTPUT_JS_DEPLOY = os.path.join(BASE_DIR, "netlify_deploy", "static", "js", "model_data.js")

def generate_worldcup_data():
    if not os.path.exists(MODEL_PATH):
        print("model.pkl not found!")
        return
        
    with open(MODEL_PATH, 'rb') as f:
        pkg = pickle.load(f)
        
    # Define the 48 World Cup 2026 Teams and their Groups (A to L)
    groups = {
        "Group A": ["USA", "Colombia", "Senegal", "Saudi Arabia"],
        "Group B": ["Mexico", "Uruguay", "South Korea", "Iran"],
        "Group C": ["Canada", "Morocco", "Japan", "Belgium"],
        "Group D": ["Argentina", "Croatia", "Australia", "Poland"],
        "Group E": ["Brazil", "Italy", "Switzerland", "Egypt"],
        "Group F": ["France", "Netherlands", "Ecuador", "Ukraine"],
        "Group G": ["England", "Portugal", "Nigeria", "Qatar"],
        "Group H": ["Spain", "Denmark", "Algeria", "Cameroon"],
        "Group I": ["Germany", "Austria", "Chile", "Iraq"],
        "Group J": ["Sweden", "Scotland", "Peru", "Tunisia"],
        "Group K": ["Turkey", "Wales", "Paraguay", "Ghana"],
        "Group L": ["Hungary", "Czechia", "Venezuela", "Ivory Coast"]
    }
    
    # Establish International Elos
    elos = {
        "Argentina": 2150.0, "France": 2110.0, "Spain": 2100.0, "England": 2050.0,
        "Brazil": 2020.0, "Portugal": 2000.0, "Netherlands": 1980.0, "Italy": 1970.0,
        "Germany": 1960.0, "Colombia": 1950.0, "Uruguay": 1940.0, "Croatia": 1920.0,
        "Belgium": 1900.0, "Morocco": 1880.0, "Denmark": 1850.0, "Japan": 1860.0,
        "Switzerland": 1840.0, "Senegal": 1840.0, "USA": 1820.0, "Sweden": 1820.0,
        "Ukraine": 1810.0, "Austria": 1810.0, "Mexico": 1800.0, "Ecuador": 1800.0,
        "Turkey": 1800.0, "Poland": 1790.0, "Australia": 1790.0, "Hungary": 1790.0,
        "Canada": 1780.0, "South Korea": 1780.0, "Chile": 1780.0, "Nigeria": 1780.0,
        "Czechia": 1770.0, "Algeria": 1770.0, "Ivory Coast": 1770.0, "Scotland": 1760.0,
        "Cameroon": 1760.0, "Iran": 1760.0, "Egypt": 1760.0, "Peru": 1750.0,
        "Ghana": 1750.0, "Paraguay": 1740.0, "Wales": 1740.0, "Venezuela": 1730.0,
        "Tunisia": 1730.0, "Saudi Arabia": 1720.0, "Qatar": 1710.0, "Iraq": 1690.0
    }
    
    # Generate Elo Trajectories (last 30 matches history)
    elo_history = {}
    for team, elo in elos.items():
        elo_history[team] = []
        current_elo = elo - 60.0 # start slightly lower
        for i in range(30):
            # random walk to simulate Elo changes over matches
            current_elo += random.uniform(-15, 20)
            date_str = f"202{4 + (i // 12)}-{(i % 12) + 1:02d}-15"
            elo_history[team].append({'date': date_str, 'elo': float(current_elo)})
        # Make final one match exactly current Elo
        elo_history[team][-1]['elo'] = float(elo)
        
    # Generate strengths
    strengths = {}
    for team, elo in elos.items():
        # Strengths scale with Elo
        factor = elo / 1500.0
        strengths[team] = {
            'att_home': float(factor * 1.1),
            'def_home': float(2.0 - factor * 0.9),
            'att_away': float(factor * 0.95),
            'def_away': float(2.0 - factor * 0.85),
            'avg_shots': float(8.0 + factor * 5.0),
            'avg_corners': float(3.0 + factor * 3.0),
            'avg_yellow': float(1.2 + random.uniform(0.2, 0.8)),
            'avg_red': float(0.02 + random.uniform(0.01, 0.05))
        }
        
    # Generate mock head-to-head records
    h2h_history = {}
    teams_list = list(elos.keys())
    for i in range(len(teams_list)):
        for j in range(i + 1, len(teams_list)):
            t1 = teams_list[i]
            t2 = teams_list[j]
            key = f"{t1}__{t2}" if t1 < t2 else f"{t2}__{t1}"
            
            # Seed 2 matches
            g1_t1 = int(random.choices([0, 1, 2, 3], weights=[30, 40, 20, 10])[0])
            g1_t2 = int(random.choices([0, 1, 2, 3], weights=[35, 40, 15, 10])[0])
            g2_t1 = int(random.choices([0, 1, 2, 3], weights=[35, 40, 15, 10])[0])
            g2_t2 = int(random.choices([0, 1, 2, 3], weights=[30, 40, 20, 10])[0])
            
            h2h_history[key] = [
                {'home': t1, 'away': t2, 'home_goals': g1_t1, 'away_goals': g1_t2},
                {'home': t2, 'away': t1, 'home_goals': g2_t2, 'away_goals': g2_t1}
            ]
            
    # Mock team history (rolling features: [points, goals_scored, goals_conceded])
    team_history = {}
    for team in elos:
        team_history[team] = []
        for _ in range(5):
            pts = random.choice([3, 1, 0])
            gf = random.choice([0, 1, 2, 3])
            ga = random.choice([0, 1, 2])
            team_history[team].append([pts, gf, ga])

    # Player Registry & detailed chronological Match Logs
    players = [
        {
            "name": "Lionel Messi", "country": "Argentina", "rating": 9.1, "position": "Forward",
            "goals": 106, "assists": 56, "matches": 180, "yellow": 8, "red": 1,
            "club": "Inter Miami", "age": 38,
            "match_history": [
                {"date": "2026-03-22", "match": "Argentina vs Uruguay", "result": "W 2-1", "rating": 8.4, "goals": 1, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-17", "match": "Argentina vs Peru", "result": "W 3-0", "rating": 9.2, "goals": 2, "assists": 0, "minutes": 82, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-18", "match": "Brazil vs Argentina", "result": "L 0-1", "rating": 7.6, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-13", "match": "Argentina vs Paraguay", "result": "W 2-0", "rating": 8.8, "goals": 1, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-16", "match": "Peru vs Argentina", "result": "W 0-2", "rating": 9.5, "goals": 2, "assists": 0, "minutes": 90, "yellow_cards": 1, "red_cards": 0}
            ]
        },
        {
            "name": "Cristiano Ronaldo", "country": "Portugal", "rating": 8.7, "position": "Forward",
            "goals": 128, "assists": 46, "matches": 205, "yellow": 26, "red": 0,
            "club": "Al Nassr", "age": 41,
            "match_history": [
                {"date": "2026-03-24", "match": "Portugal vs Sweden", "result": "W 3-1", "rating": 8.1, "goals": 1, "assists": 0, "minutes": 78, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-19", "match": "Portugal vs Poland", "result": "W 2-0", "rating": 7.8, "goals": 1, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-19", "match": "Croatia vs Portugal", "result": "D 1-1", "rating": 7.2, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-14", "match": "Portugal vs Poland", "result": "W 5-1", "rating": 9.4, "goals": 2, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-15", "match": "Scotland vs Portugal", "result": "D 0-0", "rating": 6.9, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 1, "red_cards": 0}
            ]
        },
        {
            "name": "Kylian Mbappé", "country": "France", "rating": 9.0, "position": "Forward",
            "goals": 46, "assists": 30, "matches": 77, "yellow": 4, "red": 0,
            "club": "Real Madrid", "age": 27,
            "match_history": [
                {"date": "2026-03-23", "match": "France vs Germany", "result": "L 0-2", "rating": 7.1, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-18", "match": "France vs Chile", "result": "W 3-2", "rating": 8.7, "goals": 1, "assists": 2, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-21", "match": "Greece vs France", "result": "D 2-2", "rating": 8.0, "goals": 1, "assists": 0, "minutes": 64, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-16", "match": "France vs Gibraltar", "result": "W 14-0", "rating": 10.0, "goals": 3, "assists": 3, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-13", "match": "Netherlands vs France", "result": "W 1-2", "rating": 9.2, "goals": 2, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0}
            ]
        },
        {
            "name": "Jude Bellingham", "country": "England", "rating": 8.9, "position": "Midfielder",
            "goals": 6, "assists": 8, "matches": 29, "yellow": 2, "red": 0,
            "club": "Real Madrid", "age": 22,
            "match_history": [
                {"date": "2026-03-26", "match": "England vs Belgium", "result": "D 2-2", "rating": 8.9, "goals": 1, "assists": 0, "minutes": 90, "yellow_cards": 1, "red_cards": 0},
                {"date": "2026-03-21", "match": "England vs Brazil", "result": "L 0-1", "rating": 7.4, "goals": 0, "assists": 0, "minutes": 67, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-20", "match": "North Macedonia vs England", "result": "D 1-1", "rating": 7.0, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-17", "match": "England vs Malta", "result": "W 2-0", "rating": 7.6, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-17", "match": "England vs Italy", "result": "W 3-1", "rating": 9.1, "goals": 0, "assists": 2, "minutes": 85, "yellow_cards": 0, "red_cards": 0}
            ]
        },
        {
            "name": "Vinícius Júnior", "country": "Brazil", "rating": 8.8, "position": "Forward",
            "goals": 5, "assists": 6, "matches": 28, "yellow": 4, "red": 0,
            "club": "Real Madrid", "age": 25,
            "match_history": [
                {"date": "2026-03-26", "match": "Spain vs Brazil", "result": "D 3-3", "rating": 8.2, "goals": 0, "assists": 1, "minutes": 82, "yellow_cards": 1, "red_cards": 0},
                {"date": "2026-03-21", "match": "England vs Brazil", "result": "W 0-1", "rating": 7.9, "goals": 0, "assists": 0, "minutes": 89, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-22", "match": "Brazil vs Argentina", "result": "L 0-1", "rating": 6.8, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-17", "match": "Colombia vs Brazil", "result": "L 2-1", "rating": 7.4, "goals": 0, "assists": 1, "minutes": 27, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-18", "match": "Uruguay vs Brazil", "result": "L 2-0", "rating": 6.5, "goals": 0, "assists": 0, "minutes": 84, "yellow_cards": 0, "red_cards": 0}
            ]
        },
        {
            "name": "Lamine Yamal", "country": "Spain", "rating": 8.8, "position": "Forward",
            "goals": 3, "assists": 5, "matches": 14, "yellow": 0, "red": 0,
            "club": "Barcelona", "age": 18,
            "match_history": [
                {"date": "2026-03-26", "match": "Spain vs Brazil", "result": "D 3-3", "rating": 9.0, "goals": 0, "assists": 2, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-22", "match": "Spain vs Colombia", "result": "L 0-1", "rating": 7.2, "goals": 0, "assists": 0, "minutes": 72, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-19", "match": "Spain vs Georgia", "result": "W 3-1", "rating": 8.3, "goals": 0, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-16", "match": "Cyprus vs Spain", "result": "W 1-3", "rating": 8.8, "goals": 1, "assists": 0, "minutes": 40, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-12", "match": "Spain vs Scotland", "result": "W 2-0", "rating": 7.5, "goals": 0, "assists": 0, "minutes": 45, "yellow_cards": 0, "red_cards": 0}
            ]
        },
        {
            "name": "Harry Kane", "country": "England", "rating": 8.7, "position": "Forward",
            "goals": 62, "assists": 19, "matches": 89, "yellow": 6, "red": 0,
            "club": "Bayern Munich", "age": 32,
            "match_history": [
                {"date": "2026-03-26", "match": "England vs Belgium", "result": "D 2-2", "rating": 7.4, "goals": 0, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-21", "match": "England vs Brazil", "result": "L 0-1", "rating": 6.8, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-20", "match": "North Macedonia vs England", "result": "D 1-1", "rating": 7.5, "goals": 1, "assists": 0, "minutes": 32, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-17", "match": "England vs Malta", "result": "W 2-0", "rating": 8.2, "goals": 1, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-17", "match": "England vs Italy", "result": "W 3-1", "rating": 9.4, "goals": 2, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0}
            ]
        },
        {
            "name": "Mohamed Salah", "country": "Egypt", "rating": 8.6, "position": "Forward",
            "goals": 54, "assists": 32, "matches": 96, "yellow": 2, "red": 0,
            "club": "Liverpool", "age": 33,
            "match_history": [
                {"date": "2026-03-21", "match": "Egypt vs Senegal", "result": "W 1-0", "rating": 8.3, "goals": 1, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-16", "match": "Burkina Faso vs Egypt", "result": "W 1-2", "rating": 7.9, "goals": 0, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-19", "match": "Sierra Leone vs Egypt", "result": "W 0-2", "rating": 7.5, "goals": 0, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-15", "match": "Egypt vs Djibouti", "result": "W 6-0", "rating": 10.0, "goals": 4, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-16", "match": "Egypt vs Algeria", "result": "D 1-1", "rating": 7.1, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0}
            ]
        },
        {
            "name": "Christian Pulisic", "country": "USA", "rating": 8.5, "position": "Forward",
            "goals": 28, "assists": 17, "matches": 64, "yellow": 7, "red": 0,
            "club": "AC Milan", "age": 27,
            "match_history": [
                {"date": "2026-03-24", "match": "USA vs Mexico", "result": "W 2-0", "rating": 8.8, "goals": 1, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-19", "match": "USA vs Jamaica", "result": "W 3-1", "rating": 8.2, "goals": 0, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-21", "match": "Trinidad & Tobago vs USA", "result": "L 2-1", "rating": 6.9, "goals": 0, "assists": 0, "minutes": 90, "yellow_cards": 1, "red_cards": 0},
                {"date": "2025-11-16", "match": "USA vs Trinidad & Tobago", "result": "W 3-0", "rating": 8.4, "goals": 1, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-18", "match": "USA vs Ghana", "result": "W 4-0", "rating": 8.9, "goals": 1, "assists": 1, "minutes": 75, "yellow_cards": 0, "red_cards": 0}
            ]
        },
        {
            "name": "Son Heung-min", "country": "South Korea", "rating": 8.5, "position": "Forward",
            "goals": 44, "assists": 22, "matches": 123, "yellow": 6, "red": 0,
            "club": "Tottenham Hotspur", "age": 33,
            "match_history": [
                {"date": "2026-03-26", "match": "Thailand vs South Korea", "result": "W 0-3", "rating": 8.6, "goals": 1, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2026-03-21", "match": "South Korea vs Thailand", "result": "D 1-1", "rating": 8.0, "goals": 1, "assists": 0, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-21", "match": "China vs South Korea", "result": "W 0-3", "rating": 9.3, "goals": 2, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-11-16", "match": "South Korea vs Singapore", "result": "W 5-0", "rating": 8.9, "goals": 1, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0},
                {"date": "2025-10-17", "match": "South Korea vs Vietnam", "result": "W 6-0", "rating": 8.8, "goals": 1, "assists": 1, "minutes": 90, "yellow_cards": 0, "red_cards": 0}
            ]
        }
    ]
    
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
        'current_elos': elos,
        'elo_history': elo_history,
        'team_history': team_history,
        'h2h_history': h2h_history,
        'strengths': strengths,
        'avg_hg': float(pkg['avg_hg']),
        'avg_ag': float(pkg['avg_ag']),
        'groups': groups,
        'manual': manual_payload,
        'forest': forest,
        'players': players
    }
    
    # Write as a JavaScript variable assignment
    js_content = f"// Automatically generated database for FIFA World Cup 2026 Portal\nconst MODEL_DATA = {json.dumps(model_data, indent=2)};\n"
    
    # Write to static folder
    os.makedirs(os.path.dirname(OUTPUT_JS), exist_ok=True)
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Successfully exported World Cup data to {OUTPUT_JS} ({len(js_content)} bytes).")
    
    # Write to netlify_deploy folder
    os.makedirs(os.path.dirname(OUTPUT_JS_DEPLOY), exist_ok=True)
    with open(OUTPUT_JS_DEPLOY, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Successfully exported World Cup data to {OUTPUT_JS_DEPLOY} ({len(js_content)} bytes).")

if __name__ == "__main__":
    generate_worldcup_data()
