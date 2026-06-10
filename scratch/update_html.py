import os
import re

html_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Navigation Tabs
new_nav = """<nav class="app-nav">
                <button class="nav-tab active" id="tab-home" onclick="switchTab('home')">Home</button>
                <button class="nav-tab" id="tab-live" onclick="switchTab('live')">Live Tracking of FIFA'26</button>
                <button class="nav-tab" id="tab-standings" onclick="switchTab('standings')">Standings Players</button>
                <button class="nav-tab" id="tab-prediction" onclick="switchTab('prediction')">AI Prediction</button>
                <button class="nav-tab" id="tab-tournaments" onclick="switchTab('tournaments')">Tournaments Schedule</button>
                <button class="nav-tab" id="tab-news" onclick="switchTab('news')">News Update</button>
                <button class="nav-tab" id="tab-history" onclick="switchTab('history')">Player match history</button>
            </nav>"""
html = re.sub(r'<nav class="app-nav">.*?</nav>', new_nav, html, flags=re.DOTALL)

# 2. Append New Sections before </main>
new_sections = """
        <section id="section-home" class="content-section active">
            <h2 style="text-align:center; color: var(--accent-brand); margin-bottom: 2rem;">Welcome to the Home Dashboard</h2>
            <p style="text-align:center; color: var(--text-muted);">Please select a specific module above to begin tracking, predicting, and analyzing.</p>
        </section>
        
        <section id="section-news" class="content-section" style="display:none;">
            <div class="glass-card">
                <h2 style="color:var(--accent-brand); border-bottom: 1px solid var(--border-color); padding-bottom:1rem; margin-bottom:1rem;">Live News Update</h2>
                <div class="timeline-event"><strong>BREAKING:</strong> FIFA '26 groups confirmed. Top seeds prepare for grueling group stages.</div>
                <div class="timeline-event"><strong>UPDATE:</strong> AI models predict highest scoring tournament in history due to expanded format.</div>
                <div class="timeline-event"><strong>INJURY REPORT:</strong> Key players closely monitored as domestic leagues conclude.</div>
            </div>
        </section>

        <section id="section-history" class="content-section" style="display:none;">
            <div class="glass-card">
                <h2 style="color:var(--accent-brand); border-bottom: 1px solid var(--border-color); padding-bottom:1rem; margin-bottom:1rem;">Player Match History Logs</h2>
                <table class="group-standings-table" style="width:100%; text-align:left;">
                    <thead>
                        <tr><th>Date</th><th>Match</th><th>Rating</th><th>Goals</th><th>Assists</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Jun 12, 2026</td><td>USA vs COL</td><td>8.5</td><td>1</td><td>0</td></tr>
                        <tr><td>Jun 15, 2026</td><td>USA vs CRO</td><td>7.9</td><td>0</td><td>1</td></tr>
                        <tr><td>Jun 18, 2026</td><td>USA vs ARG</td><td>9.1</td><td>2</td><td>0</td></tr>
                    </tbody>
                </table>
            </div>
        </section>
"""

# Replace the existing sections with the new ones by changing their IDs to match the tabs
html = html.replace('id="section-simulator"', 'id="section-live" style="display:none;"')
html = html.replace('id="section-players"', 'id="section-standings" style="display:none;"')
html = html.replace('id="section-predictor"', 'id="section-prediction" style="display:none;"')
html = html.replace('id="section-leaderboards"', 'id="section-tournaments" style="display:none;"')
# Manual section can be hidden completely as it wasn't requested
html = html.replace('id="section-manual"', 'id="section-manual" style="display:none;"')

# Inject home, news, history
html = html.replace('</main>', new_sections + '\n</main>')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated index.html")
