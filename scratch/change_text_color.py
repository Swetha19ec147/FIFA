import os

css_path = r"C:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css"

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Change white text colors to black
css = css.replace("--text-primary: #ffffff;", "--text-primary: #000000;")
css = css.replace("--text-secondary: #e0e6ed;", "--text-secondary: #333333;")
css = css.replace("--text-muted: #8b9bb4;", "--text-muted: #555555;")
css = css.replace("color: #ffffff !important;", "color: #000000 !important;")
css = css.replace("color: #ffffff;", "color: #000000;")

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

print("Updated text colors to black.")
