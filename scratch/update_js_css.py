import os
import re

# 1. UPDATE CSS
css_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css"
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Change accents to Neon Green
css = re.sub(r"--accent-brand:\s*#ffcc00;", "--accent-brand: #00FF41;", css)
css = re.sub(r"--accent-gold:\s*#ffaa00;", "--accent-gold: #00FF41;", css)
css = re.sub(r"rgba\(255, 204, 0,", "rgba(0, 255, 65,", css)
css = re.sub(r"rgba\(255, 193, 7,", "rgba(0, 255, 65,", css)
css = re.sub(r"linear-gradient\(135deg, #ffcc00, #ffaa00\)", "linear-gradient(135deg, #00FF41, #00C832)", css)
css = re.sub(r"linear-gradient\(135deg, #ffdd33, #ffcc00\)", "linear-gradient(135deg, #33FF66, #00FF41)", css)

# Make darks darker (Black/Charcoal theme)
css = re.sub(r"--bg-body:\s*#050a14;", "--bg-body: #050505;", css)
css = re.sub(r"--bg-card:\s*rgba\(15, 20, 35, 0.75\);", "--bg-card: rgba(10, 10, 10, 0.85);", css)
css = re.sub(r"--bg-card-hover:\s*rgba\(25, 35, 55, 0.85\);", "--bg-card-hover: rgba(20, 20, 20, 0.95);", css)

# Add 3D neon glow
css = css.replace("box-shadow: 0 40px 80px -20px rgba(0, 255, 65, 0.15)", "box-shadow: 0 40px 80px -20px rgba(0, 255, 65, 0.4), 0 0 30px rgba(0, 255, 65, 0.2)")

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

# 2. UPDATE JS
js_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\static\js\app.js"
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Replace switchTab
new_switch = """function switchTab(tabId) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
    
    document.getElementById('tab-' + tabId).classList.add('active');
    const section = document.getElementById('section-' + tabId);
    if(section) {
        section.style.display = 'block';
    }
}"""
js = re.sub(r"function switchTab\(tabId\) \{.*?\}(?=\n\n)", new_switch, js, flags=re.DOTALL)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)

print("Updated JS and CSS.")
