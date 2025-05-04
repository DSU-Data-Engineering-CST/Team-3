import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("VIDEO_ID")
API_URL = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={VIDEO_ID}&key={YOUTUBE_API_KEY}"

def fetch_views():
    response = requests.get(API_URL)
    data = response.json()
    views = data['items'][0]['statistics']['viewCount']
    return views

while True:
    views = fetch_views()
    timestamp = pd.Timestamp.now()
    df = pd.DataFrame({'timestamp': [timestamp], 'views': [views]})
    if not os.path.exists('views.csv'):
        df.to_csv('views.csv', index=False)
    else:
        df.to_csv('views.csv', mode='a', header=False, index=False)
    print(f"✅ Views saved at {timestamp}")
    time.sleep(60)
