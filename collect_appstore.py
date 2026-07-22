"""Collect Blinkit App Store reviews via Apple's public RSS feed -> CSV.

Uses the iTunes customer-reviews RSS endpoint (stable, no scraping library).
Caps at ~500 recent reviews (10 pages x 50).
"""
import time
import requests
import pandas as pd
import config

RSS = ("https://itunes.apple.com/{country}/rss/customerreviews/"
       "page={page}/id={app_id}/sortby=mostrecent/json")


def fetch_appstore():
    rows = []
    for page in range(1, config.APPSTORE_MAX_PAGES + 1):
        url = RSS.format(country=config.REVIEW_COUNTRY, page=page,
                         app_id=config.APPSTORE_APP_ID)
        try:
            resp = requests.get(url, timeout=20,
                                headers={"User-Agent": "research-script/1.0"})
            resp.raise_for_status()
            entries = resp.json().get("feed", {}).get("entry", [])
        except Exception as e:
            print(f"  page {page} failed: {e}")
            break
        # First entry is sometimes app metadata (no im:rating) - skip those
        page_reviews = [e for e in entries if "im:rating" in e]
        if not page_reviews:
            break
        for e in page_reviews:
            rows.append({
                "source": "appstore",
                "review_id": e.get("id", {}).get("label"),
                "rating": int(e.get("im:rating", {}).get("label", 0)),
                "date": e.get("updated", {}).get("label"),
                "title": e.get("title", {}).get("label", ""),
                "text": e.get("content", {}).get("label", "").strip(),
                "app_version": e.get("im:version", {}).get("label"),
            })
        print(f"  page {page}: {len(page_reviews)} reviews")
        time.sleep(1)
    df = pd.DataFrame(rows).drop_duplicates("review_id")
    df.to_csv(config.OUT_APPSTORE, index=False)
    print(f"Saved {len(df)} App Store reviews -> {config.OUT_APPSTORE}")
    return df


if __name__ == "__main__":
    fetch_appstore()
