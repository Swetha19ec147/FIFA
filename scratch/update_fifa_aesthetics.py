import os

css_path = r"c:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css"
netlify_css = r"c:\Users\aspire\OneDrive\Desktop\Fifa\netlify_deploy\static\css\styles.css"

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Add new CSS rules
extra_css = """
/* =========================================
   EXTRAORDINARY FIFA AESTHETICS & ANIMATIONS
   ========================================= */

/* Parallax Stadium Background */
body {
    background-image: linear-gradient(to bottom, rgba(10, 15, 36, 0.8), rgba(10, 15, 36, 1)), url('/static/img/parallax_stadium.png');
    background-size: cover;
    background-attachment: fixed;
    background-position: center top;
}

/* Floating Animations for Cards */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}

.timeline-event, .player-card, .group-card {
    animation: float 6s ease-in-out infinite;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.timeline-event:nth-child(even) {
    animation-delay: 1.5s;
}

/* Intense Neon Hover Glows */
.timeline-event:hover, .player-card:hover, .group-card:hover, .match-item:hover {
    transform: translateY(-12px) scale(1.02) !important;
    box-shadow: 0 15px 35px rgba(255, 0, 85, 0.3), 0 0 20px rgba(255, 215, 0, 0.2);
    border-color: var(--accent-magenta);
    z-index: 10;
}

/* Staggered Slide In for Sections */
@keyframes slideUpFade {
    from {
        opacity: 0;
        transform: translateY(40px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.content-section {
    animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Glowing Pulse for Live Elements */
@keyframes intensePulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.7); }
    70% { box-shadow: 0 0 0 15px rgba(255, 0, 85, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }
}

.live-dot.pulse {
    animation: intensePulse 2s infinite;
    background: var(--accent-magenta);
}

/* Neon Text Accents */
h1, h2, h3, .nav-tab {
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}

.nav-tab.active {
    color: var(--accent-gold) !important;
    text-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
    border-bottom: 3px solid var(--accent-gold);
}

/* Custom Variables Update */
:root {
    --accent-magenta: #FF0055;
    --accent-neon-blue: #00F0FF;
    --accent-gold: #FFD700;
}
"""

# Append if not already present
if "EXTRAORDINARY FIFA AESTHETICS" not in css:
    css += extra_css

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

with open(netlify_css, "w", encoding="utf-8") as f:
    f.write(css)

print("Cinematic CSS animations applied.")
