import os
import re

html_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Mini Predictor (Home Screen)
html = html.replace('<div class="mini-predictor-layout">', '<div class="mini-predictor-layout" id="pre-match-result">')
html = html.replace('<select class="custom-select"><option>United States</option></select>', '<select class="custom-select" id="home-select"><option>United States</option></select>')
html = html.replace('<select class="custom-select"><option>Colombia</option></select>', '<select class="custom-select" id="away-select"><option>Colombia</option></select>')
html = html.replace('<button class="btn btn-primary" style="width:100%; margin-top:1rem;">CALCULATE AI FORECAST</button>', '<button class="btn btn-primary" id="btn-calculate-predictions" style="width:100%; margin-top:1rem;">CALCULATE AI FORECAST</button>')

html = html.replace('<div class="bar-fill" style="width:48%; background:var(--neon-lime)"></div>', '<div class="bar-fill" id="bar-prob-home" style="width:48%; background:var(--neon-lime)"></div>')
html = html.replace('<div class="bar-fill" style="width:25%; background:#888"></div>', '<div class="bar-fill" id="bar-prob-draw" style="width:25%; background:#888"></div>')
html = html.replace('<div class="bar-fill" style="width:27%; background:var(--neon-red)"></div>', '<div class="bar-fill" id="bar-prob-away" style="width:27%; background:var(--neon-red)"></div>')

html = html.replace('<span>48%</span>', '<span id="lbl-prob-home">48%</span>', 1)
html = html.replace('<span>25%</span>', '<span id="lbl-prob-draw">25%</span>', 1)
html = html.replace('<span>27%</span>', '<span id="lbl-prob-away">27%</span>', 1)

html = html.replace('<div class="score-number">2 - 1</div>', '<div class="score-number" id="lbl-predicted-score">2 - 1</div>')
html = html.replace('<div class="xg-text">xG 1.8 vs 0.9</div>', '<div class="xg-text">xG <span id="lbl-xg-home">1.8</span> vs <span id="lbl-xg-away">0.9</span></div>')

# 2. Main Predictor Hub
html = html.replace('<select class="custom-select"><option>USA</option></select>', '<select class="custom-select" id="home-select-hub"><option>USA</option></select>')
html = html.replace('<select class="custom-select"><option>COLOMBIA</option></select>', '<select class="custom-select" id="away-select-hub"><option>COLOMBIA</option></select>')

# Link insights table
html = html.replace('<table class="insights-table">', '<table class="insights-table" id="prediction-factors-container">')

# Powerplayer 
html = html.replace('<div class="panel profile-panel">', '<div class="panel profile-panel" id="powerplayer-dashboard">')
html = html.replace('<div class="player-rating-badge">9.2</div>', '<div class="player-rating-badge" id="lbl-powerplayer-rating">9.2</div>')
html = html.replace('<div class="panel-header">Powerplayer of the Match</div>', '<div class="panel-header">Powerplayer: <span id="lbl-powerplayer-name">Player</span></div><div style="font-size:0.8rem; color:var(--text-muted);" id="lbl-powerplayer-reason"></div>')

# 3. Leaderboards
html = html.replace('<tr><td>1</td><td>🇦🇷 Argentina</td><td style="color:var(--neon-lime)">3225</td></tr>\n                    <tr><td>2</td><td>🇫🇷 France</td><td style="color:var(--neon-lime)">3190</td></tr>\n                    <tr><td>3</td><td>🇧🇷 Brazil</td><td style="color:var(--neon-lime)">3150</td></tr>', '<tbody id="team-leaderboard-body"></tbody>')

# Write back
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Injected dynamic IDs into index.html")
