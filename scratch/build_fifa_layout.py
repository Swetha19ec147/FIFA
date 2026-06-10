import os
import re

html_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\templates\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update the Header to be sticky and add Hero Section
hero_section = """
    <!-- FIFA.COM STYLE HERO CAROUSEL -->
    <div class="fifa-hero-banner">
        <div class="fifa-hero-content">
            <div class="hero-tag">FIFA World Cup 26™</div>
            <h1 class="hero-title-main">PREDICT. SIMULATE. DOMINATE.</h1>
            <p class="hero-desc">Experience the ultimate AI-powered Match Center. Live tracking, Elo forecasts, and real-time brackets for the 48-nation tournament.</p>
            <div class="hero-buttons">
                <a href="#section-predictor" class="btn btn-primary" style="text-decoration:none;">Launch AI Predictor</a>
                <a href="#section-simulator" class="btn btn-outline" style="text-decoration:none; color:white; border-color:white;">Live Match Center</a>
            </div>
        </div>
        <div class="hero-gradient-overlay"></div>
    </div>
"""
# Insert hero section right after header
html = re.sub(r'(</header>)', r'\1\n' + hero_section, html)

# 2. Add Horizontal Scrolling Match Strip (already have Match Schedule List Carousel, let's keep it but move it under the hero)
# The existing one is right after <header>, so the hero will be inserted BEFORE the schedule carousel since we matched </header>.
# Wait, the schedule carousel is currently right after </header>. The above regex puts hero between header and schedule. That is perfect.

# 3. Make the nav buttons anchor links and remove onclick='switchTab()'
# Actually, I can just modify switchTab in app.js so I don't have to rewrite all the HTML buttons.

# 4. Remove display:none from sections so they stack vertically
html = re.sub(r'style="display:\s*none;?"', '', html)
# Except for some inner toggles like tourney-view-live which need to stay hidden initially
# Wait, replacing all `display:none` might break the simulator inner tabs.
# Let's specifically target the main sections:
html = html.replace('<section id="section-simulator" class="content-section" >', '<section id="section-simulator" class="content-section">')
html = html.replace('<section id="section-players" class="content-section" >', '<section id="section-players" class="content-section">')
html = html.replace('<section id="section-leaderboards" class="content-section" >', '<section id="section-leaderboards" class="content-section">')
html = html.replace('<section id="section-manual" class="content-section" >', '<section id="section-manual" class="content-section">')
# I'll just use regex for the sections
html = re.sub(r'(<section id="section-[a-z]+" class="content-section".*?)style="display:\s*none;?"', r'\1', html)

# 5. Add a News/Video Section to mimic FIFA.com (just mockup cards)
news_section = """
    <section id="section-news" class="content-section">
        <h2 style="font-size:2rem; margin-bottom:1.5rem; border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;">Latest News & Highlights</h2>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
            <div class="glass-card" style="padding:0; overflow:hidden;">
                <div style="height:200px; background: url('/static/img/stadium_bg.png') center/cover;"></div>
                <div style="padding:1rem;">
                    <div style="font-size:0.8rem; color:var(--accent-gold); margin-bottom:0.5rem;">TOURNAMENT NEWS</div>
                    <h3 style="margin-bottom:0.5rem;">Groups Drawn for 48-Team Format</h3>
                    <p style="color:var(--text-muted); font-size:0.9rem;">The path to glory is set. Check out the group stage matchups in the Live Center.</p>
                </div>
            </div>
            <div class="glass-card" style="padding:0; overflow:hidden;">
                <div style="height:200px; background: url('/static/img/player_visionary.png') center/cover;"></div>
                <div style="padding:1rem;">
                    <div style="font-size:0.8rem; color:var(--accent-gold); margin-bottom:0.5rem;">PLAYER FOCUS</div>
                    <h3 style="margin-bottom:0.5rem;">Mbappé Eyes Golden Boot</h3>
                    <p style="color:var(--text-muted); font-size:0.9rem;">With the expanded tournament, top strikers are looking to break scoring records.</p>
                </div>
            </div>
            <div class="glass-card" style="padding:0; overflow:hidden;">
                <div style="height:200px; background: #111; display:flex; align-items:center; justify-content:center;">▶</div>
                <div style="padding:1rem;">
                    <div style="font-size:0.8rem; color:var(--accent-gold); margin-bottom:0.5rem;">VIDEO HIGHLIGHTS</div>
                    <h3 style="margin-bottom:0.5rem;">AI Predicts Shock Final</h3>
                    <p style="color:var(--text-muted); font-size:0.9rem;">Watch our latest simulation breakdown of the knockout bracket.</p>
                </div>
            </div>
        </div>
    </section>
"""
html = html.replace('</main>', news_section + '\n</main>')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)


# UPDATE CSS for the new Hero and Sticky Header
css_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css"
with open(css_path, "a", encoding="utf-8") as f:
    f.write("""
/* FIFA.COM LAYOUT OVERRIDES */
.app-header {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(10, 10, 15, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border-color);
}
.fifa-hero-banner {
    position: relative;
    height: 60vh;
    min-height: 500px;
    background: url('/static/img/stadium_bg.png') center/cover;
    display: flex;
    align-items: center;
    padding: 0 4rem;
    margin-bottom: 2rem;
}
.hero-gradient-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to right, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 50%, transparent 100%);
    z-index: 1;
}
.fifa-hero-content {
    position: relative;
    z-index: 2;
    max-width: 600px;
}
.hero-tag {
    background: var(--accent-brand);
    color: #000;
    display: inline-block;
    padding: 0.25rem 0.75rem;
    font-weight: 800;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.85rem;
}
.hero-title-main {
    font-size: 4rem;
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 1rem;
    text-transform: uppercase;
}
.hero-desc {
    font-size: 1.1rem;
    color: #ccc;
    margin-bottom: 2rem;
}
.hero-buttons {
    display: flex;
    gap: 1rem;
}
.content-section {
    margin-bottom: 4rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 2rem;
}
""")

# UPDATE JS so switchTab smooth scrolls instead of hiding
js_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\static\js\app.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

new_switch = """function switchTab(tabId) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    const section = document.getElementById('section-' + tabId);
    if(section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}"""
js = re.sub(r"function switchTab\(tabId\) \{.*?\}(?=\n\n)", new_switch, js, flags=re.DOTALL)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)

print("Updated HTML, CSS, and JS to implement FIFA.com scrolling layout.")
