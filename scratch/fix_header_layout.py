import os
import re

html_files = [
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\index.html",
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\netlify_deploy\index.html"
]

for html_file in html_files:
    if not os.path.exists(html_file):
        continue
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    # Enhance semantic HTML and SEO
    old_nav = """<nav class="app-nav">
                <button class="nav-tab active" id="tab-predictor" onclick="switchTab('predictor')">AI Predictor</button>"""
    new_nav = """<nav class="app-nav" aria-label="Main Navigation" role="navigation">
                <button class="nav-tab active" id="tab-predictor" onclick="switchTab('predictor')" aria-selected="true">AI Predictor</button>"""
    html = html.replace(old_nav, new_nav)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

css_files = [
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css",
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\netlify_deploy\static\css\styles.css"
]

for css_file in css_files:
    if not os.path.exists(css_file):
        continue
    with open(css_file, "r", encoding="utf-8") as f:
        css = f.read()

    header_css = """
/* NEAT HEADER OVERHAUL - SPACIOUS & MOBILE FRIENDLY */
.app-header {
    position: sticky !important;
    top: 0 !important;
    z-index: 1000 !important;
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border-color) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important;
    transition: all 0.3s ease !important;
}

.header-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 1rem 2rem !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    gap: 2rem !important;
}

.app-nav {
    display: flex !important;
    gap: 2rem !important;
    align-items: center !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
    white-space: nowrap !important;
    padding-bottom: 0px !important;
}

.app-nav::-webkit-scrollbar {
    display: none !important;
}

.nav-tab {
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    font-family: var(--font-heading) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 0 !important;
    cursor: pointer !important;
    position: relative !important;
    transition: color 0.3s ease, transform 0.3s ease !important;
}

.nav-tab::after {
    content: '' !important;
    position: absolute !important;
    bottom: -5px !important;
    left: 0 !important;
    width: 0% !important;
    height: 3px !important;
    background: var(--accent-brand) !important;
    transition: width 0.3s ease !important;
    border-radius: 2px !important;
}

.nav-tab:hover {
    color: var(--text-main) !important;
    transform: translateY(-2px) !important;
}

.nav-tab:hover::after {
    width: 50% !important;
}

.nav-tab.active {
    color: var(--accent-brand) !important;
    background: transparent !important;
    border-bottom: none !important; /* using the animated ::after instead */
}

.nav-tab.active::after {
    width: 100% !important;
    box-shadow: 0 2px 8px rgba(0, 177, 106, 0.4) !important;
}

/* 3D Animated Logo Hover */
.logo-area {
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    cursor: pointer !important;
    perspective: 1000px !important;
}
.logo-area:hover {
    transform: rotateX(5deg) rotateY(-5deg) scale(1.05) !important;
}
.logo-text {
    display: flex !important;
    flex-direction: column !important;
}
.brand-name {
    font-family: var(--font-heading) !important;
    font-weight: 900 !important;
    font-size: 1.5rem !important;
    color: var(--text-main) !important;
    line-height: 1 !important;
}
.sub-brand {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: var(--accent-brand) !important;
    letter-spacing: 2px !important;
}

@media (max-width: 768px) {
    .header-container {
        flex-direction: column !important;
        padding: 1rem !important;
        gap: 1rem !important;
    }
    .app-nav {
        width: 100% !important;
        justify-content: flex-start !important;
        padding-bottom: 0.5rem !important;
    }
}
"""
    if "/* NEAT HEADER OVERHAUL" not in css:
        css += header_css

    with open(css_file, "w", encoding="utf-8") as f:
        f.write(css)

print("Header layout overhauled.")
