import os

target_files = [
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\static\js\app.js",
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\netlify_deploy\static\js\app.js"
]

for file_path in target_files:
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Patch 1: Replace loadPlayersData to use API_BASE
    old_load = """async function loadPlayersData() {
    try {
        const response = await fetch('/static/data/players_db.json');
        GLOBAL_PLAYERS_DB = await response.json();
    } catch (err) {
        console.warn("Failed to load players_db.json, using fallback mocks.", err);
    }
}"""
    
    new_load = """async function loadPlayersData() {
    try {
        const response = await fetch(`${API_BASE}/players`);
        if (response.ok) {
            GLOBAL_PLAYERS_DB = await response.json();
        } else {
            console.warn("Failed to load players from backend");
        }
    } catch (err) {
        console.warn("Backend unavailable for players data.", err);
    }
}"""
    content = content.replace(old_load, new_load)
    
    # Patch 2: Add initMatchSchedule logic inside DOMContentLoaded
    old_init = """document.addEventListener('DOMContentLoaded', () => {
    loadPlayersData().then(() => {
        populateLeaderboards();
    });
    initLiveTrackingSSE();
});"""

    new_init = """
async function initMatchSchedule() {
    try {
        const response = await fetch(`${API_BASE}/schedule`);
        if(response.ok) {
            const data = await response.json();
            const container = document.getElementById('ticker-wrapper');
            if (container && data.schedule) {
                container.innerHTML = '';
                data.schedule.forEach(match => {
                    container.innerHTML += `<div class="ticker-item"><span class="live-dot pulse"></span> ${match.home} vs ${match.away} | ${match.date} | ${match.stadium}</div>`;
                });
            }
        }
    } catch(err) {
        console.error("Live Tracker Schedule failed:", err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadPlayersData().then(() => {
        populateLeaderboards();
    });
    initMatchSchedule();
    
    // Setup live polling every 10 seconds for real-time tracking
    setInterval(() => {
        initMatchSchedule();
    }, 10000);
});"""

    content = content.replace(old_init, new_init)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Frontend API patches applied.")
