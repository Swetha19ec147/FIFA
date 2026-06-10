import os

css_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css"

css_content = """
:root {
    --bg-body: #0a0a0a;
    --bg-card: #151515;
    --bg-card-hover: #1e1e1e;
    --border-color: #2a2a2a;
    --text-primary: #ffffff;
    --text-muted: #888888;
    --neon-lime: #caff00;
    --neon-green: #00ff41;
    --neon-red: #ff3333;
    --font-inter: 'Inter', sans-serif;
    --font-outfit: 'Outfit', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: var(--font-inter);
    background-color: var(--bg-body);
    color: var(--text-primary);
    overflow-x: hidden;
}

/* TOP TICKER */
.top-ticker {
    background: #000;
    border-bottom: 1px solid var(--border-color);
    padding: 0.5rem 2rem;
    font-size: 0.8rem;
    font-weight: 600;
    display: flex;
    gap: 3rem;
    overflow: hidden;
    white-space: nowrap;
}

/* HEADER */
.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--border-color);
    background: #0a0a0a;
}
.nav-links {
    display: flex;
    gap: 2rem;
}
.nav-link {
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    transition: 0.3s;
}
.nav-link:hover, .nav-link.active {
    color: var(--neon-lime);
}
.live-badge {
    color: var(--neon-red);
    font-weight: 800;
    font-size: 0.8rem;
}

/* CONTAINER */
.dashboard-container {
    max-width: 1400px;
    margin: 2rem auto;
    padding: 0 2rem;
}

/* HERO */
.hero-banner {
    text-align: center;
    padding: 4rem 0;
    background: radial-gradient(circle at center, #1a2315 0%, #0a0a0a 70%);
    border-radius: 12px;
    margin-bottom: 2rem;
}
.hero-title {
    font-family: var(--font-outfit);
    font-size: 4rem;
    font-weight: 800;
    margin: 1rem 0;
    text-transform: uppercase;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto 2rem;
}
.hero-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 3rem;
}
.hero-flags {
    display: flex;
    gap: 1rem;
    justify-content: center;
}
.flag-box {
    background: var(--bg-card);
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-weight: 600;
}

/* BUTTONS */
.btn {
    padding: 1rem 2rem;
    font-family: var(--font-inter);
    font-weight: 700;
    border-radius: 50px;
    cursor: pointer;
    text-transform: uppercase;
    transition: 0.3s;
    border: none;
}
.btn-primary {
    background: var(--neon-lime);
    color: #000;
    box-shadow: 0 0 20px rgba(202, 255, 0, 0.2);
}
.btn-primary:hover {
    box-shadow: 0 0 30px rgba(202, 255, 0, 0.4);
    transform: translateY(-2px);
}
.btn-outline {
    background: transparent;
    color: var(--neon-lime);
    border: 2px solid var(--neon-lime);
}

/* PANELS */
.panel {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    transition: transform 0.3s;
}
.panel:hover {
    border-color: var(--neon-lime);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.panel-header {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #fff;
}

/* GRIDS */
.home-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-top: 2rem;
}
.predictor-hub-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}
.grid-span-2 {
    grid-column: span 2;
}

/* SCHEDULE */
.schedule-carousel {
    display: flex;
    gap: 1rem;
    overflow-x: auto;
    padding-bottom: 1rem;
}
.schedule-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    min-width: 250px;
    padding: 1rem;
}
.active-card {
    border-color: var(--neon-lime);
}
.schedule-header {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
}
.schedule-teams {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 700;
    font-size: 1.2rem;
    margin-bottom: 1rem;
}
.schedule-footer {
    font-size: 0.75rem;
    color: var(--text-muted);
}

/* ENGINE */
.engine-layout {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #0d0d0d;
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
}
.vs-glow {
    color: var(--neon-lime);
    font-size: 2rem;
    font-weight: 800;
    text-shadow: 0 0 20px var(--neon-lime);
}
.massive-prob-bar {
    height: 30px;
    background: #222;
    border-radius: 15px;
    display: flex;
    overflow: hidden;
}
.segment.home { background: var(--neon-lime); }
.segment.draw { background: #555; }
.segment.away { background: var(--neon-red); }

/* TABLES */
.insights-table { width: 100%; border-collapse: collapse; }
.insights-table th, .insights-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border-color); }
.insights-table td.high { color: var(--neon-lime); font-weight: 700; }

.standard-table { width: 100%; border-collapse: collapse; }
.standard-table th { color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; text-align: left; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-color); }
.standard-table td { padding: 0.75rem 0; border-bottom: 1px solid #1a1a1a; }

/* MASS GRID (LIVE CENTER) */
.mass-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}
.mass-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
}
.mass-header {
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--neon-lime);
}
.mass-table { width: 100%; margin-bottom: 1rem; }
.mass-table td { padding: 0.25rem 0; font-size: 0.9rem; }
"""

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content)

print("styles.css successfully overwritten with the specific tactical screenshot layout styling.")
