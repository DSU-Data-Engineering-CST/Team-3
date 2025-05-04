import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("VIDEO_ID")
API_URL = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={VIDEO_ID}&key={YOUTUBE_API_KEY}"

def fetch_likes():
    response = requests.get(API_URL)
    data = response.json()
    likes = data['items'][0]['statistics'].get('likeCount', 0)
    return likes

while True:
    likes = fetch_likes()
    timestamp = pd.Timestamp.now()
    df = pd.DataFrame({'timestamp': [timestamp], 'likes': [likes]})
    if not os.path.exists('likes.csv'):
        df.to_csv('likes.csv', index=False)
    else:
        df.to_csv('likes.csv', mode='a', header=False, index=False)
    print(f"✅ Likes saved at {timestamp}")
    time.sleep(60)
