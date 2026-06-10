import os

target_files = [
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css",
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\netlify_deploy\static\css\styles.css"
]

for file_path in target_files:
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    old_css = """.content-section {
    display: none;
}

.content-section.active {
    display: block;
    animation: fadeIn 0.35s ease-out;
}"""

    # If exact block is not found, we can also just regex it
    import re
    # Remove display: none for content-section
    content = re.sub(r'\.content-section\s*\{\s*display:\s*none;\s*\}', '', content)
    content = re.sub(r'\.content-section\.active\s*\{\s*display:\s*block;\s*animation:[^\}]+\}', '', content)
    
    # We also need to fix switchTab so that it forces display block just in case
    # actually, with the CSS removed, all sections are block by default.
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("CSS patches applied.")
