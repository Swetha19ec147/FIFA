import re

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Find all function definitions: function name(...)
defined_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', code))
print("Defined functions:", sorted(defined_funcs))

# Find all function calls: name(...)
# We match word characters followed by (
# To avoid matching keywords like if, for, while, switch, catch, etc., we filter them.
keywords = {'if', 'for', 'while', 'switch', 'catch', 'function', 'let', 'const', 'var', 'return', 'else', 'new', 'typeof'}
called_funcs = set()
for match in re.finditer(r'\b([a-zA-Z0-9_]+)\s*\(', code):
    name = match.group(1)
    if name not in keywords and not name[0].isdigit():
        called_funcs.add(name)

print("\nCalled functions:", sorted(called_funcs))

# Find calls to functions not defined
standard_js = {
    'alert', 'parseInt', 'Math', 'Array', 'Float64Array', 'setInterval', 
    'clearInterval', 'setTimeout', 'log', 'error', 'find', 'forEach', 
    'reduce', 'map', 'push', 'splice', 'slice', 'indexOf', 'sort', 
    'localeCompare', 'addEventListener', 'getElementById', 'querySelectorAll', 
    'createElement', 'appendChild', 'querySelector', 'remove', 'insertBefore', 
    'Chart', 'fetch', 'json', 'decode', 'toString', 'toFixed', 'isNaN', 'hasAttribute'
}
undefined_calls = called_funcs - defined_funcs - standard_js
print("\nUndefined function calls (excluding standard JS and arrays):", sorted(undefined_calls))
