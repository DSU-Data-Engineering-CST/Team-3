import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("VIDEO_ID")
API_URL = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={VIDEO_ID}&key={YOUTUBE_API_KEY}"

def fetch_comments():
    response = requests.get(API_URL)
    data = response.json()
    comments = data['items'][0]['statistics'].get('commentCount', 0)
    return comments

while True:
    comments = fetch_comments()
    timestamp = pd.Timestamp.now()
    df = pd.DataFrame({'timestamp': [timestamp], 'comments': [comments]})
    if not os.path.exists('comments.csv'):
        df.to_csv('comments.csv', index=False)
    else:
        df.to_csv('comments.csv', mode='a', header=False, index=False)
    print(f"✅ Comments saved at {timestamp}")
    time.sleep(60)
