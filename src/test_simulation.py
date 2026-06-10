import os
import sys
import json

# Set console output encoding to UTF-8 to handle emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Setup sys path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from app import app

def simulate_full_match(home="Man City", away="Arsenal"):
    print(f"=== STARTING AUTOMATED LIVE SIMULATION: {home} VS {away} ===")
    
    # Configure app for testing client
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Pre-match prediction
    pre_payload = {'home_team': home, 'away_team': away}
    pre_resp = client.post('/api/predict', data=json.dumps(pre_payload), content_type='application/json')
    pre_data = json.loads(pre_resp.data.decode('utf-8'))
    
    pre_pred = pre_data['prediction']
    print(f"Pre-Match Forecast: {home} Win: {pre_pred['home_win_prob']*100:.1f}% | Draw: {pre_pred['draw_prob']*100:.1f}% | {away} Win: {pre_pred['away_win_prob']*100:.1f}%")
    print(f"Predicted Final Score: {pre_pred['predicted_score']} (xG: {pre_pred['expected_goals_home']:.2f} - {pre_pred['expected_goals_away']:.2f})")
    print("-" * 70)
    
    # Initialize match state
    match_state = {
        'home_team': home,
        'away_team': away,
        'minute': 0,
        'home_goals': 0,
        'away_goals': 0,
        'home_red_cards': 0,
        'away_red_cards': 0,
        'home_shots': 0,
        'away_shots': 0,
        'home_sot': 0,
        'away_sot': 0,
        'home_corners': 0,
        'away_corners': 0,
        'home_fouls': 0,
        'away_fouls': 0
    }
    
    # Run simulation step-by-step
    for minute in range(1, 91):
        match_state['minute'] = minute
        
        # Call simulation step endpoint
        resp = client.post('/api/simulate-step', data=json.dumps(match_state), content_type='application/json')
        data = json.loads(resp.data.decode('utf-8'))
        
        if not data['success']:
            print(f"Error at minute {minute}: {data.get('error')}")
            break
            
        # Update our simulation state from the returned API stats
        match_state.update(data['stats'])
        
        # Log events
        for event in data['events']:
            print(f"[{event['type'].upper()}] {event['desc']}")
            
        # Log status at key intervals (15', 30', 45' HT, 60', 75', 90' FT)
        if minute in [15, 30, 45, 60, 75, 90]:
            h_prob = data['prediction']['home_win_prob'] * 100
            d_prob = data['prediction']['draw_prob'] * 100
            a_prob = data['prediction']['away_win_prob'] * 100
            
            label = f"{minute}'"
            if minute == 45: label = "45' (Half-Time)"
            elif minute == 90: label = "90' (Full-Time)"
            
            print(f"⏱️ {label} | Score: {home} {match_state['home_goals']} - {match_state['away_goals']} {away}")
            print(f"   AI Win Probability Live: {home} {h_prob:.1f}% | Draw {d_prob:.1f}% | {away} {a_prob:.1f}%")
            print("-" * 50)
            
    print("\n=== MATCH STATISTICS SUMMARY ===")
    print(f"Possession: {match_state['possession_home']}% vs {match_state['possession_away']}%")
    print(f"Shots: {match_state['home_shots']} vs {match_state['away_shots']}")
    print(f"Shots on Target: {match_state['home_sot']} vs {match_state['away_sot']}")
    print(f"Corners: {match_state['home_corners']} vs {match_state['away_corners']}")
    print(f"Red Cards: {match_state['home_red_cards']} vs {match_state['away_red_cards']}")
    print(f"Final Score: {home} {match_state['home_goals']} - {match_state['away_goals']} {away}")
    print("======================================================================\n")

if __name__ == "__main__":
    simulate_full_match()
