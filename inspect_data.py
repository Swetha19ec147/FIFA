import urllib.request
import pandas as pd
import io
import os

url = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
print(f"Downloading from {url}...")

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read()
    
    df = pd.read_csv(io.BytesIO(html))
    print("Download successful!")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns)[:25])
    print("\nFirst 3 rows:")
    print(df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']].head(3))
except Exception as e:
    print("Error:", e)
