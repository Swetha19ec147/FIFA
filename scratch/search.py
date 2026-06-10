import os

def search_word_in_files(word, directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.js') or file.endswith('.py') or file.endswith('.html'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if word in line:
                                print(f"Found '{word}' in {path}:{i} -> {line.strip()[:100]}")
                except Exception as e:
                    pass

search_word_in_files("simulateStep", "c:\\Users\\aspire\\OneDrive\\Desktop\\Fifa")
