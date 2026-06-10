import os

html_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\templates\index.html"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIFA 26 AI Predictor Hub</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <!-- Live Ticker -->
    <div class="top-ticker">
        <span>USA 0-0 COL <span style="color:var(--neon-red)">● LIVE</span></span>
        <span>ARG 2-1 CRO</span>
        <span>FRA 3-1 NED</span>
        <span>BRA 2-0 ITA</span>
        <span>ENG 1-0 POR</span>
        <span>ESP 2-2 DEN</span>
        <span>GER 3-0 CHI</span>
    </div>

    <!-- Main Navigation -->
    <header class="main-header">
        <div class="logo">
            <span style="color: var(--neon-lime); font-size: 1.5rem;">🏆</span>
            <span style="font-weight: 800; font-size: 1.25rem;">FIFA 26</span>
        </div>
        <nav class="nav-links">
            <a href="#" class="nav-link active" onclick="switchTab('home')">HOME</a>
            <a href="#" class="nav-link" onclick="switchTab('predictor')">AI PREDICTOR</a>
            <a href="#" class="nav-link" onclick="switchTab('livecenter')">LIVE CENTER</a>
            <a href="#" class="nav-link" onclick="switchTab('players')">PLAYERS</a>
            <a href="#" class="nav-link" onclick="switchTab('leaderboard')">LEADERBOARD</a>
        </nav>
        <div class="live-badge">● LIVE</div>
    </header>

    <main class="dashboard-container">
        <!-- HOME DASHBOARD (Matches Image 3) -->
        <section id="section-home" class="dashboard-section active">
            <div class="hero-banner">
                <div class="hero-content">
                    <h4 style="color:var(--neon-lime); letter-spacing: 2px;">FIFA WORLD CUP 2026</h4>
                    <h1 class="hero-title">PREDICT. SIMULATE. DOMINATE.</h1>
                    <p class="hero-sub">AI-powered match forecasting for all 48 nations. Elo ratings. Live brackets. Player intelligence.</p>
                    <div class="hero-actions">
                        <button class="btn btn-primary" onclick="switchTab('predictor')">RUN AI PREDICTOR</button>
                        <button class="btn btn-outline" onclick="switchTab('livecenter')">WATCH LIVE SCORES</button>
                    </div>
                    <div class="hero-flags">
                        <div class="flag-box">🇺🇸 USA</div>
                        <div class="flag-box">🇧🇷 BRA</div>
                        <div class="flag-box">🇫🇷 FRA</div>
                        <div class="flag-box">🇦🇷 ARG</div>
                        <div class="flag-box">🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENG</div>
                        <div class="flag-box">🇪🇸 ESP</div>
                    </div>
                </div>
            </div>
            
            <h3 class="section-title">Match Schedule</h3>
            <div class="schedule-carousel">
                <div class="schedule-card">
                    <div class="schedule-header">GROUP A • 11 JUN 2026</div>
                    <div class="schedule-teams">
                        <div class="team"><span class="flag">🇺🇸</span> USA</div>
                        <div class="vs">VS</div>
                        <div class="team"><span class="flag">🇨🇴</span> COL</div>
                    </div>
                    <div class="schedule-footer">SoFi Stadium, Los Angeles</div>
                </div>
                <div class="schedule-card active-card">
                    <div class="schedule-header">GROUP C • 13 JUN 2026</div>
                    <div class="schedule-teams">
                        <div class="team"><span class="flag">🇦🇷</span> ARG</div>
                        <div class="vs" style="color:var(--neon-lime)">VS</div>
                        <div class="team"><span class="flag">🇭🇷</span> CRO</div>
                    </div>
                    <div class="schedule-footer" style="color:var(--neon-lime)">MetLife Stadium, NY</div>
                </div>
                <div class="schedule-card">
                    <div class="schedule-header">GROUP D • 14 JUN 2026</div>
                    <div class="schedule-teams">
                        <div class="team"><span class="flag">🇫🇷</span> FRA</div>
                        <div class="vs">VS</div>
                        <div class="team"><span class="flag">🇳🇱</span> NED</div>
                    </div>
                    <div class="schedule-footer">AT&T Stadium, Dallas</div>
                </div>
            </div>

            <div class="home-grid">
                <!-- AI Predictor Mini -->
                <div class="panel">
                    <div class="panel-header">AI PREDICTION ENGINE</div>
                    <div class="mini-predictor-layout">
                        <div class="team-selects">
                            <select class="custom-select"><option>United States</option></select>
                            <div class="vs-circle">VS</div>
                            <select class="custom-select"><option>Colombia</option></select>
                            <button class="btn btn-primary" style="width:100%; margin-top:1rem;">CALCULATE AI FORECAST</button>
                        </div>
                        <div class="mini-predictor-results">
                            <div class="prob-bars">
                                <div class="prob-row"><span>HOME WIN</span> <div class="bar-bg"><div class="bar-fill" style="width:48%; background:var(--neon-lime)"></div></div> <span>48%</span></div>
                                <div class="prob-row"><span>DRAW</span> <div class="bar-bg"><div class="bar-fill" style="width:25%; background:#888"></div></div> <span>25%</span></div>
                                <div class="prob-row"><span>AWAY WIN</span> <div class="bar-bg"><div class="bar-fill" style="width:27%; background:var(--neon-red)"></div></div> <span>27%</span></div>
                            </div>
                            <div class="predicted-score-box">
                                <div class="score-title">PREDICTED SCORE</div>
                                <div class="score-number">2 - 1</div>
                                <div class="xg-text">xG 1.8 vs 0.9</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Knockout Bracket -->
                <div class="panel">
                    <div class="panel-header" style="display:flex; justify-content:space-between">
                        KNOCKOUT BRACKET
                        <button class="btn-text">VIEW FULL BRACKET</button>
                    </div>
                    <div class="bracket-mockup">
                        <div class="bracket-col">
                            <div class="match-box">🇺🇸 USA<br>🇳🇱 NED</div>
                            <div class="match-box">🇦🇷 ARG<br>🇦🇺 AUS</div>
                        </div>
                        <div class="bracket-col">
                            <div class="match-box highlight-match">🇺🇸 USA<br>🇦🇷 ARG</div>
                        </div>
                        <div class="bracket-col">
                            <div class="match-box final-match">🏆<br>FINAL</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- AI PREDICTOR HUB (Matches Image 1) -->
        <section id="section-predictor" class="dashboard-section" style="display:none;">
            <div class="dashboard-title-row">
                <span style="font-size: 2rem; color: var(--neon-lime);">🏆</span>
                <h2>FIFA 26 TRACKER / AI PREDICTOR HUB</h2>
            </div>
            
            <div class="predictor-hub-grid">
                <!-- Engine -->
                <div class="panel grid-span-2">
                    <div class="panel-header">The Predictor Engine</div>
                    <p class="panel-sub">Stadium-screen styled input widget for AI predictor hub.</p>
                    
                    <div class="engine-layout">
                        <div class="engine-team">
                            <label>Home Team</label>
                            <select class="custom-select"><option>USA</option></select>
                        </div>
                        <div class="engine-vs">
                            <div class="vs-glow">VS</div>
                        </div>
                        <div class="engine-team">
                            <label>Away Team</label>
                            <select class="custom-select"><option>COLOMBIA</option></select>
                        </div>
                    </div>
                    
                    <div class="engine-probs">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; font-weight:700;">
                            <span>HOME WIN %</span><span>DRAW %</span><span>AWAY WIN %</span>
                        </div>
                        <div class="massive-prob-bar">
                            <div class="segment home" style="width: 45%;"></div>
                            <div class="segment draw" style="width: 25%;"></div>
                            <div class="segment away" style="width: 30%;"></div>
                        </div>
                    </div>
                </div>

                <!-- Insights -->
                <div class="panel">
                    <div class="panel-header">AI Prediction Insights</div>
                    <table class="insights-table">
                        <tr><th>Analytics</th><th>ART</th><th>ELO</th><th>H2H</th></tr>
                        <tr><td>Elo</td><td class="high">0.27</td><td class="high">0.38</td><td>0.36</td></tr>
                        <tr><td>H2H</td><td>0.32</td><td class="high">0.38</td><td>0.25</td></tr>
                        <tr><td>WxH</td><td class="high">0.58</td><td>0.32</td><td class="high">0.53</td></tr>
                    </table>
                </div>

                <!-- Powerplayer -->
                <div class="panel profile-panel">
                    <div class="panel-header">Powerplayer of the Match</div>
                    <div class="player-silhouette">
                        <img src="/static/img/player_visionary.png" class="sil-img">
                    </div>
                    <div class="player-rating-badge">9.2</div>
                </div>

                <!-- Match Center -->
                <div class="panel grid-span-2">
                    <div class="panel-header">Live Tournament Match Center</div>
                    <div class="group-tabs">
                        <span class="g-tab active">A</span><span class="g-tab">B</span><span class="g-tab">C</span><span class="g-tab">D</span>
                    </div>
                    <table class="standard-table">
                        <tr><th>Group</th><th>Fixtures</th></tr>
                        <tr><td>Group A</td><td>🇺🇸 USA 2-3 COL 🇨🇴</td></tr>
                        <tr><td>Group B</td><td>🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENG 1-0 POR 🇵🇹</td></tr>
                        <tr><td>Group C</td><td>🇦🇷 ARG 2-1 CRO 🇭🇷</td></tr>
                    </table>
                </div>

                <!-- Live Stats -->
                <div class="panel">
                    <div class="panel-header">Real-Time Live Stats Analytics</div>
                    <div class="stat-row">
                        <div class="stat-label">Possession</div>
                        <div class="stat-bar"><div class="fill" style="width:60%"></div></div>
                        <div class="stat-val">60%</div>
                    </div>
                    <div class="stat-row">
                        <div class="stat-label">Shots</div>
                        <div class="stat-bar"><div class="fill" style="width:40%"></div></div>
                        <div class="stat-val">15</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- LIVE CENTER (Matches Image 2) -->
        <section id="section-livecenter" class="dashboard-section" style="display:none;">
            <div class="panel-header" style="text-align:center; font-size:1.5rem; color:var(--neon-lime); margin-bottom:1rem;">LIVE TOURNAMENT CENTER</div>
            <div class="mass-grid">
                <div class="mass-panel">
                    <div class="mass-header">GROUP A</div>
                    <table class="mass-table">
                        <tr><td>1. USA</td><td>9</td></tr>
                        <tr><td>2. COL</td><td>6</td></tr>
                        <tr><td>3. WAL</td><td>3</td></tr>
                    </table>
                    <button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem;">SIMULATION</button>
                </div>
                <div class="mass-panel">
                    <div class="mass-header">GROUP B</div>
                    <table class="mass-table">
                        <tr><td>1. ENG</td><td>9</td></tr>
                        <tr><td>2. POR</td><td>4</td></tr>
                        <tr><td>3. KOR</td><td>4</td></tr>
                    </table>
                    <button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem;">SIMULATION</button>
                </div>
                <!-- Add 10 more to simulate the massive grid -->
                <div class="mass-panel"><div class="mass-header">GROUP C</div><button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem; margin-top:auto;">SIMULATION</button></div>
                <div class="mass-panel"><div class="mass-header">GROUP D</div><button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem; margin-top:auto;">SIMULATION</button></div>
                <div class="mass-panel"><div class="mass-header">GROUP E</div><button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem; margin-top:auto;">SIMULATION</button></div>
                <div class="mass-panel"><div class="mass-header">GROUP F</div><button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem; margin-top:auto;">SIMULATION</button></div>
                <div class="mass-panel"><div class="mass-header">GROUP G</div><button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem; margin-top:auto;">SIMULATION</button></div>
                <div class="mass-panel"><div class="mass-header">GROUP H</div><button class="btn btn-primary" style="width:100%; padding: 0.5rem; font-size: 0.8rem; margin-top:auto;">SIMULATION</button></div>
            </div>
            <button class="btn btn-primary" style="display:block; margin: 2rem auto; width: 300px;">SIMULATE ALL GROUPS</button>
        </section>

        <!-- PLAYERS & LEADERBOARD -->
        <section id="section-players" class="dashboard-section" style="display:none;">
            <div class="panel">
                <div class="panel-header">ELITE PLAYERS HUB</div>
                <div style="display:flex; gap: 2rem;">
                    <div class="player-sil-card">
                        <img src="/static/img/player_visionary.png" style="width:100px; border-radius:50%; border:2px solid var(--neon-lime);">
                        <h3>Kylian Mbappé</h3>
                        <p>France • Forward</p>
                    </div>
                    <div class="match-log" style="flex:1;">
                        <table class="standard-table">
                            <tr><th>Match</th><th>Rating</th><th>Goals</th></tr>
                            <tr><td>FRA vs NED</td><td>9.5</td><td>2</td></tr>
                            <tr><td>FRA vs AUS</td><td>8.8</td><td>1</td></tr>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <section id="section-leaderboard" class="dashboard-section" style="display:none;">
            <div class="panel">
                <div class="panel-header">GLOBAL LEADERBOARDS</div>
                <table class="standard-table">
                    <tr><th>Rank</th><th>Team</th><th>Elo</th></tr>
                    <tr><td>1</td><td>🇦🇷 Argentina</td><td style="color:var(--neon-lime)">3225</td></tr>
                    <tr><td>2</td><td>🇫🇷 France</td><td style="color:var(--neon-lime)">3190</td></tr>
                    <tr><td>3</td><td>🇧🇷 Brazil</td><td style="color:var(--neon-lime)">3150</td></tr>
                </table>
            </div>
        </section>
    </main>

    <script src="/static/js/app.js"></script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("index.html successfully overwritten with the massive new grid layout.")
