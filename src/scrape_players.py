import os
import json
import requests
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

TEAMS = [
    "Argentina", "France", "Spain", "England", "Brazil", "Portugal", "Netherlands",
    "Italy", "Germany", "Colombia", "Uruguay", "Croatia", "Belgium", "USA"
]

def fetch_players():
    print("Fetching player data from TheSportsDB (Open Endpoint v1)...")
    players_data = {}
    
    # Generic fallback photos for when players don't have images
    generic_photo = "/static/img/player_visionary.png"
    
    for team in TEAMS:
        print(f"Fetching {team}...")
        try:
            url = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?t={requests.utils.quote(team)}"
            res = requests.get(url, timeout=10)
            data = res.json()
            
            team_players = []
            if data and data.get("player"):
                # Take up to 15 top players per team
                for p in data["player"][:15]:
                    photo_url = p.get("strCutout") or p.get("strThumb") or generic_photo
                    # Prefer smaller/compressed images or just use URL directly
                    team_players.append({
                        "name": p.get("strPlayer", "Unknown Player"),
                        "position": p.get("strPosition", "Midfielder"),
                        "photo": photo_url,
                        "team": team,
                        "rating": round(8.0 + (float(p.get("idPlayer", 0)) % 18) / 10.0, 1) # mock rating 8.0-9.8
                    })
            else:
                # Fallback mock data if API fails or team not found
                print(f"No players found for {team}. Using mock data.")
                team_players = [
                    {"name": f"{team} Star 1", "position": "Forward", "photo": generic_photo, "team": team, "rating": 9.2},
                    {"name": f"{team} Star 2", "position": "Midfielder", "photo": generic_photo, "team": team, "rating": 8.7},
                    {"name": f"{team} Star 3", "position": "Defender", "photo": generic_photo, "team": team, "rating": 8.5}
                ]
                
            players_data[team] = team_players
            time.sleep(1) # Rate limit respect
            
        except Exception as e:
            print(f"Failed to fetch {team}: {e}")
            players_data[team] = [
                {"name": f"{team} Generic Player", "position": "Forward", "photo": generic_photo, "team": team, "rating": 8.5}
            ]

    # Flatten the dictionary if needed, but keeping it grouped by team is useful
    out_path = os.path.join(DATA_DIR, "players_db.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(players_data, f, indent=4)
        
    print(f"Successfully saved players to {out_path}")

if __name__ == "__main__":
    fetch_players()
