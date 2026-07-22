"""Collect Zepto + BigBasket reviews (Play + App Store) for the cross-platform
benchmark. No keys needed. -> data/competitor_reviews.csv (with a platform tag).
"""
import time
import requests
import pandas as pd
from google_play_scraper import reviews, Sort
import config

RSS = ("https://itunes.apple.com/{country}/rss/customerreviews/"
       "page={page}/id={app_id}/sortby=mostrecent/json")


def play(platform, app_id):
    rows, token, pulled = [], None, 0
    while pulled < config.COMPETITOR_PLAYSTORE_TARGET:
        batch = min(200, config.COMPETITOR_PLAYSTORE_TARGET - pulled)
        result, token = reviews(app_id, lang=config.REVIEW_LANG,
                                country=config.REVIEW_COUNTRY, sort=Sort.NEWEST,
                                count=batch, continuation_token=token)
        if not result:
            break
        for r in result:
            rows.append({"platform": platform, "source": "playstore",
                         "review_id": r.get("reviewId"), "rating": r.get("score"),
                         "date": r.get("at"), "text": (r.get("content") or "").strip()})
        pulled += len(result)
        if token is None:
            break
        time.sleep(1)
    print(f"  {platform} playstore: {len(rows)}")
    return rows


def appstore(platform, app_id):
    rows = []
    for page in range(1, config.COMPETITOR_APPSTORE_MAX_PAGES + 1):
        url = RSS.format(country=config.REVIEW_COUNTRY, page=page, app_id=app_id)
        try:
            entries = requests.get(url, timeout=20,
                                   headers={"User-Agent": "research/1.0"}
                                   ).json().get("feed", {}).get("entry", [])
        except Exception as e:
            print(f"    {platform} appstore p{page} failed: {e}")
            break
        revs = [e for e in entries if "im:rating" in e]
        if not revs:
            break
        for e in revs:
            rows.append({"platform": platform, "source": "appstore",
                         "review_id": e.get("id", {}).get("label"),
                         "rating": int(e.get("im:rating", {}).get("label", 0)),
                         "date": e.get("updated", {}).get("label"),
                         "text": e.get("content", {}).get("label", "").strip()})
        time.sleep(1)
    print(f"  {platform} appstore: {len(rows)}")
    return rows


def main():
    allrows = []
    for platform, ids in config.COMPETITORS.items():
        print(platform)
        allrows += play(platform, ids["playstore"])
        allrows += appstore(platform, ids["appstore"])
    df = pd.DataFrame(allrows).drop_duplicates("review_id")
    df = df[df["text"].str.len() > 0]
    df.to_csv(config.OUT_COMPETITORS, index=False)
    print(f"Saved {len(df)} competitor reviews -> {config.OUT_COMPETITORS}")
    print(df.groupby(["platform", "source"]).size().to_string())


if __name__ == "__main__":
    main()
