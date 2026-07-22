"""Collect Blinkit / quick-commerce Reddit discussions -> CSV.

Setup (one time):
  1. Go to https://www.reddit.com/prefs/apps  -> create app -> type "script"
  2. Copy client_id (under the app name) and client_secret
  3. Put them in a .env file next to this script:
        REDDIT_CLIENT_ID=xxxx
        REDDIT_CLIENT_SECRET=xxxx
"""
import os
import time
import praw
import pandas as pd
from dotenv import load_dotenv
import config

load_dotenv()


def get_reddit():
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent="qc-discovery-research/1.0",
    )


def _row(source, submission, text, kind):
    return {
        "source": "reddit",
        "channel": source,
        "kind": kind,                      # post | comment
        "post_id": submission.id,
        "subreddit": str(submission.subreddit),
        "score": submission.score,
        "date": submission.created_utc,
        "text": text.strip(),
        "url": f"https://reddit.com{submission.permalink}",
    }


def fetch_reddit():
    reddit = get_reddit()
    rows, seen = [], set()

    def harvest(submission, channel):
        if submission.id in seen:
            return
        seen.add(submission.id)
        body = f"{submission.title}\n{submission.selftext or ''}"
        rows.append(_row(channel, submission, body, "post"))
        try:
            submission.comments.replace_more(limit=0)
            for c in submission.comments[:config.REDDIT_COMMENTS_PER_POST]:
                rows.append({
                    "source": "reddit", "channel": channel, "kind": "comment",
                    "post_id": submission.id, "subreddit": str(submission.subreddit),
                    "score": c.score, "date": c.created_utc,
                    "text": (c.body or "").strip(),
                    "url": f"https://reddit.com{submission.permalink}",
                })
        except Exception as e:
            print(f"    comments failed for {submission.id}: {e}")

    # 1) Global keyword search across all of Reddit
    for q in config.REDDIT_QUERIES:
        print(f"  search r/all: {q!r}")
        try:
            for s in reddit.subreddit("all").search(q, limit=config.REDDIT_POST_LIMIT,
                                                     sort="relevance"):
                harvest(s, f"search:{q}")
        except Exception as e:
            print(f"    query failed: {e}")
        time.sleep(2)

    # 2) Targeted subreddits, searching "Blinkit" within each
    for sub in config.REDDIT_SUBREDDITS:
        print(f"  r/{sub} search 'Blinkit'")
        try:
            for s in reddit.subreddit(sub).search("Blinkit", limit=config.REDDIT_POST_LIMIT):
                harvest(s, f"r/{sub}")
        except Exception as e:
            print(f"    sub failed: {e}")
        time.sleep(2)

    df = pd.DataFrame(rows)
    df = df[df["text"].str.len() > 3].drop_duplicates(["post_id", "kind", "text"])
    df.to_csv(config.OUT_REDDIT, index=False)
    print(f"Saved {len(df)} Reddit rows -> {config.OUT_REDDIT}")
    return df


if __name__ == "__main__":
    fetch_reddit()
