from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
import os
import random
import pickle
import pandas as pd
import numpy as np

app = FastAPI(title="Visionary FIFA Predictor API", version="2.0")

# Allow Netlify frontend to communicate with local/remote backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "Visionary FIFA Predictor Backend Running"}

@app.get("/api/schedule")
def get_schedule():
    # Will be replaced with scraped FIFA '26 schedule
    return {"schedule": [
        {"date": "11 JUN 2026", "group": "A", "home": "USA", "away": "COL", "stadium": "SoFi Stadium, Los Angeles"},
        {"date": "13 JUN 2026", "group": "C", "home": "ARG", "away": "CRO", "stadium": "MetLife Stadium, NY"}
    ]}

@app.post("/api/predict")
def predict_match(req: PredictionRequest):
    try:
        model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
        with open(model_path, "rb") as f:
            model = pickle.load(f)
            
        # Mock Elo fetch for the teams
        home_elo = random.uniform(1400, 2000)
        away_elo = random.uniform(1400, 2000)
        elo_diff = home_elo - away_elo
        
        # Prepare input df
        input_data = pd.DataFrame({
            'home_elo': [home_elo],
            'away_elo': [away_elo],
            'elo_diff': [elo_diff],
            'home_form': [random.uniform(0, 1)],
            'away_form': [random.uniform(0, 1)]
        })
        
        # Output probability array [Away Win, Draw, Home Win]
        probs = model.predict_proba(input_data)[0]
        away_prob = probs[0] * 100
        draw_prob = probs[1] * 100
        home_prob = probs[2] * 100
        
        # Calculate expected goals
        xg_home = (home_prob / 100) * 3.5
        xg_away = (away_prob / 100) * 3.5
        
        predicted_score = f"{int(round(xg_home))} - {int(round(xg_away))}"
        
        return {
            "success": True,
            "prediction": {
                "home_win_prob": round(home_prob, 1),
                "draw_prob": round(draw_prob, 1),
                "away_win_prob": round(away_prob, 1),
                "expected_goals_home": round(xg_home, 2),
                "expected_goals_away": round(xg_away, 2),
                "predicted_score": predicted_score,
                "insights": {
                    "elo_advantage": req.home_team if home_elo > away_elo else req.away_team,
                    "h2h_trend": "Even",
                }
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/players")
def get_players():
    # Load from the scraped JSON DB
    db_path = os.path.join(os.path.dirname(__file__), "..", "static", "data", "players_db.json")
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Player database not generated yet."}

if __name__ == "__main__":
    # Run the server locally on port 8000
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
