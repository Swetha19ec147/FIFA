import os

css_files = [
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\static\css\styles.css",
    r"c:\Users\aspire\OneDrive\Desktop\Fifa\netlify_deploy\static\css\styles.css"
]

select2_fixes = """
/* SELECT 2 BRIGHT THEME UI FIXES */
.select2-container--default .select2-selection--single {
    background-color: #FFFFFF !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 8px !important;
    height: 50px !important;
    display: flex !important;
    align-items: center !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}

.select2-container--default.select2-container--open .select2-selection--single {
    border-color: var(--accent-brand) !important;
    box-shadow: 0 0 0 3px rgba(0, 177, 106, 0.2) !important;
}

.select2-container--default .select2-selection--single .select2-selection__rendered {
    color: var(--text-main) !important; /* Important: Deep Charcoal Text */
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding-left: 15px !important;
}

.select2-container--default .select2-selection--single .select2-selection__arrow {
    height: 48px !important;
    right: 10px !important;
}

.select2-dropdown {
    background-color: #FFFFFF !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
    overflow: hidden !important;
    margin-top: 5px !important;
}

.select2-container--default .select2-search--dropdown .select2-search__field {
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    padding: 10px !important;
    color: var(--text-main) !important;
    background: #F4F6F9 !important;
    font-family: var(--font-body) !important;
}

.select2-container--default .select2-search--dropdown .select2-search__field:focus {
    outline: none !important;
    border-color: var(--accent-brand) !important;
}

.select2-container--default .select2-results__option {
    color: var(--text-main) !important;
    padding: 12px 15px !important;
    font-weight: 500 !important;
    font-family: var(--font-body) !important;
    transition: all 0.2s ease !important;
}

.select2-container--default .select2-results__option--highlighted[aria-selected],
.select2-container--default .select2-results__option:hover {
    background-color: rgba(0, 177, 106, 0.1) !important;
    color: var(--accent-brand) !important;
}

.select2-container--default .select2-results__option[aria-selected="true"] {
    background-color: rgba(0, 177, 106, 0.05) !important;
    color: var(--text-main) !important;
    font-weight: 700 !important;
}
"""

for css_file in css_files:
    if not os.path.exists(css_file):
        continue
    with open(css_file, "r", encoding="utf-8") as f:
        css = f.read()

    if "/* SELECT 2 BRIGHT THEME UI FIXES */" not in css:
        css += select2_fixes
        with open(css_file, "w", encoding="utf-8") as f:
            f.write(css)

print("Select2 UI fixes applied successfully.")
