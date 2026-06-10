import os
import re

target_files = [
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css",
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\netlify_deploy\static\css\styles.css"
]

for file_path in target_files:
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update font imports for a cleaner professional look
    font_imports = """@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&family=Roboto:wght@300;400;500;700&display=swap');"""
    content = re.sub(r"@import url\('https://fonts\.googleapis\.com[^']+'\);", "", content)
    content = font_imports + "\n" + content

    # 2. Update CSS Variables for Bright Mode
    new_vars = """:root {
    --bg-dark: #F4F6F9; /* Off-white bright background */
    --bg-card: #FFFFFF; /* Pure white cards */
    --border-color: #E2E8F0; /* Soft grey borders */
    --text-main: #1A202C; /* Deep charcoal text */
    --text-muted: #718096;
    --accent-brand: #00B16A; /* FIFA Pitch Green */
    --accent-blue: #00308F; /* Royal Blue */
    --accent-red: #E53E3E;
    --accent-gold: #D69E2E;
    
    --font-heading: 'Montserrat', sans-serif;
    --font-body: 'Roboto', sans-serif;
}"""
    content = re.sub(r':root\s*\{[^}]+\}', '', content)
    content = new_vars + "\n" + content

    # 3. Apply Bright UI overrides and 3D hover effects
    bright_overrides = """
/* Bright Professional 3D Overrides */
body {
    background-color: var(--bg-dark) !important;
    background-image: none !important;
    color: var(--text-main) !important;
}

.portal-hero {
    background-image: linear-gradient(to bottom, rgba(0, 48, 143, 0.7), rgba(0, 177, 106, 0.4)), url('/static/img/bright_3d_stadium.png') !important;
    background-size: cover !important;
    background-attachment: fixed !important;
    background-position: center !important;
    color: #FFFFFF !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.content-section, .timeline-event, .player-card, .group-card, .stat-card, .prediction-results {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06), 0 4px 6px rgba(0,0,0,0.04) !important;
    color: var(--text-main) !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    perspective: 1000px;
}

/* Fix text colors inside cards */
.hero-title { color: #FFFFFF !important; text-shadow: 0 4px 15px rgba(0,0,0,0.3); }
h1, h2, h3, h4, .match-team { color: var(--text-main) !important; text-shadow: none !important; }
.match-score { color: var(--accent-brand) !important; }

/* 3D Hover Animations */
.timeline-event:hover, .player-card:hover, .group-card:hover, .match-item:hover {
    transform: translateY(-8px) scale(1.02) rotateX(4deg) rotateY(-2deg) !important;
    box-shadow: 0 20px 40px rgba(0, 177, 106, 0.15), 0 10px 15px rgba(0,0,0,0.05) !important;
    border-color: var(--accent-brand) !important;
    z-index: 10;
}

/* Buttons */
.btn-primary {
    background: linear-gradient(135deg, var(--accent-brand), #00d981) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 1rem 2rem !important;
    box-shadow: 0 6px 15px rgba(0, 177, 106, 0.3) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
.btn-primary:hover {
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 10px 25px rgba(0, 177, 106, 0.5) !important;
}

.live-dot.pulse {
    background: var(--accent-red) !important;
    animation: intensePulseRed 2s infinite !important;
}

/* Nav Tabs */
.nav-tab { color: #FFFFFF !important; }
.nav-tab.active {
    color: var(--accent-brand) !important;
    border-bottom: 4px solid var(--accent-brand) !important;
    text-shadow: none !important;
}

.timeline-event .text-muted { color: var(--text-muted) !important; }
"""
    # Remove old overrides
    content = re.sub(r'/\*\s*Reference UI Overrides\s*\*/.*', '', content, flags=re.DOTALL)
    content = re.sub(r'/\*\s*EXTRAORDINARY FIFA AESTHETICS & ANIMATIONS\s*\*/.*', '', content, flags=re.DOTALL)
    
    content += bright_overrides

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Bright 3D Theme applied.")
