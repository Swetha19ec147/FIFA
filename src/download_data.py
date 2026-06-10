import urllib.request
import os
import time

SEASONS = ["1819", "1920", "2021", "2122", "2223", "2324", "2425"]
DATA_DIR = "data"

def download_seasons():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for season in SEASONS:
        url = f"https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
        dest_path = os.path.join(DATA_DIR, f"E0_{season}.csv")
        
        # If the file is already downloaded and is not the current season (2425), skip it
        # 2425 is the latest season, so we might want to overwrite to get recent data if needed,
        # but for a stable pipeline, we will download if not present, and print progress.
        if os.path.exists(dest_path) and season != "2425":
            print(f"Season {season} data already exists at {dest_path}. Skipping download.")
            continue
            
        print(f"Downloading season {season} from {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                content = response.read()
            
            with open(dest_path, "wb") as f:
                f.write(content)
            print(f"Successfully saved to {dest_path} ({len(content)} bytes).")
            # Polite pause between requests
            time.sleep(1)
        except Exception as e:
            print(f"Failed to download season {season}: {e}")

if __name__ == "__main__":
    download_seasons()
