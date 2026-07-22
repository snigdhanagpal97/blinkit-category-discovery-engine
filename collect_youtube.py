"""Collect YouTube comments about quick-commerce apps via YouTube Data API v3.

Setup (one time):
  1. console.cloud.google.com -> create a project
  2. Search "YouTube Data API v3" -> Enable
  3. APIs & Services -> Credentials -> Create credentials -> API key -> copy
  4. Add to .env:  YOUTUBE_API_KEY=your_key
-> data/youtube_comments.csv (tagged by platform)
"""
import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
import config

load_dotenv()
KEY = os.environ["YOUTUBE_API_KEY"]
SEARCH = "https://www.googleapis.com/youtube/v3/search"
COMMENTS = "https://www.googleapis.com/youtube/v3/commentThreads"


def search_videos(query):
    params = {"part": "snippet", "q": query, "type": "video",
              "maxResults": config.YOUTUBE_VIDEOS_PER_QUERY,
              "regionCode": "IN", "relevanceLanguage": "en", "key": KEY}
    r = requests.get(SEARCH, params=params, timeout=20).json()
    return [it["id"]["videoId"] for it in r.get("items", [])
            if it.get("id", {}).get("videoId")]


def video_comments(vid):
    out = []
    params = {"part": "snippet", "videoId": vid,
              "maxResults": min(100, config.YOUTUBE_COMMENTS_PER_VIDEO),
              "order": "relevance", "textFormat": "plainText", "key": KEY}
    try:
        r = requests.get(COMMENTS, params=params, timeout=20)
        if r.status_code != 200:      # comments disabled / restricted
            return out
        for it in r.json().get("items", []):
            s = it["snippet"]["topLevelComment"]["snippet"]
            out.append({"video_id": vid, "text": s.get("textDisplay", "").strip(),
                        "likes": s.get("likeCount"), "date": s.get("publishedAt")})
    except Exception as e:
        print(f"    comments failed {vid}: {e}")
    return out


def main():
    rows = []
    for query, platform in config.YOUTUBE_QUERIES:
        print(f"  search: {query!r}")
        for vid in search_videos(query):
            for c in video_comments(vid):
                c.update({"platform": platform, "source": "youtube", "query": query})
                rows.append(c)
            time.sleep(0.5)
        time.sleep(1)
    df = pd.DataFrame(rows)
    df = df[df["text"].str.len() > 5].drop_duplicates(["video_id", "text"])
    df.to_csv(config.OUT_YOUTUBE, index=False)
    print(f"Saved {len(df)} YouTube comments -> {config.OUT_YOUTUBE}")
    print(df["platform"].value_counts().to_string())


if __name__ == "__main__":
    main()
