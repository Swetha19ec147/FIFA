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

    # 1. Update font imports
    font_imports = """@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');"""
    if "Oswald" not in content:
        content = font_imports + "\n" + content

    # 2. Update CSS Variables
    new_vars = """:root {
    --bg-dark: #0A0A0C;
    --bg-card: #111216;
    --border-color: #2A2B30;
    --text-main: #FFFFFF;
    --text-muted: #8E92A3;
    --accent-brand: #CCFF00; /* Neon Lime */
    --accent-green: #00B16A;
    --accent-red: #FF3333;
    --accent-gold: #FFD700;
    
    --font-heading: 'Oswald', sans-serif;
    --font-body: 'Inter', sans-serif;
}"""
    # Replace existing :root block (a simple regex to replace everything inside :root)
    # Since we appended custom variables earlier, let's just strip out old :root blocks and prepend this one.
    content = re.sub(r':root\s*\{[^}]+\}', '', content)
    content = content.replace("/* CSS Variables */", "/* CSS Variables */\n" + new_vars)
    if new_vars not in content:
        content = new_vars + "\n" + content

    # 3. Apply fonts to global styles
    content = re.sub(r"font-family:\s*[^;]+;", "font-family: var(--font-body);", content, count=1)
    
    heading_font_rule = """
h1, h2, h3, h4, h5, h6, .nav-tab, .btn-primary {
    font-family: var(--font-heading) !important;
    text-transform: uppercase;
}
"""
    if "font-family: var(--font-heading)" not in content:
        content += heading_font_rule

    # 4. Modify cards to have the specific dark look
    card_overrides = """
/* Reference UI Overrides */
.content-section, .timeline-event, .player-card, .group-card, .stat-card, .prediction-results {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    backdrop-filter: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
}

body {
    background: var(--bg-dark) !important;
}

.btn-primary {
    background: var(--accent-brand) !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.8rem 1.5rem !important;
    transition: transform 0.2s ease, filter 0.2s ease;
}
.btn-primary:hover {
    transform: translateY(-2px) !important;
    filter: brightness(1.2);
    box-shadow: 0 0 15px rgba(204, 255, 0, 0.4) !important;
}

.live-dot.pulse {
    background: var(--accent-red) !important;
    animation: intensePulseRed 2s infinite !important;
}

@keyframes intensePulseRed {
    0% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(255, 51, 51, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0); }
}

.match-score, .match-team, .bracket-team-score {
    font-family: var(--font-heading) !important;
}

/* Remove the old magenta/gold hover glows */
.timeline-event:hover, .player-card:hover, .group-card:hover, .match-item:hover {
    border-color: var(--accent-brand) !important;
    box-shadow: 0 5px 15px rgba(204, 255, 0, 0.1) !important;
    transform: translateY(-4px) scale(1.01) !important;
}
"""
    if "/* Reference UI Overrides */" not in content:
        content += card_overrides

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Reference UI formatting applied.")
