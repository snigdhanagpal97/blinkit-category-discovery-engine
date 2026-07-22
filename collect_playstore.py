"""Collect Blinkit Play Store reviews (paginated) -> CSV."""
import time
import pandas as pd
from google_play_scraper import reviews, Sort
import config


def fetch_playstore():
    all_rows, token, pulled = [], None, 0
    while pulled < config.PLAYSTORE_TARGET:
        batch = min(200, config.PLAYSTORE_TARGET - pulled)
        result, token = reviews(
            config.PLAYSTORE_APP_ID,
            lang=config.REVIEW_LANG,
            country=config.REVIEW_COUNTRY,
            sort=Sort.NEWEST,
            count=batch,
            continuation_token=token,
        )
        if not result:
            break
        for r in result:
            all_rows.append({
                "source": "playstore",
                "review_id": r.get("reviewId"),
                "rating": r.get("score"),
                "date": r.get("at"),
                "text": (r.get("content") or "").strip(),
                "thumbs_up": r.get("thumbsUpCount"),
                "app_version": r.get("reviewCreatedVersion"),
            })
        pulled += len(result)
        print(f"  pulled {pulled} reviews...")
        if token is None:
            break
        time.sleep(1)  # be polite
    df = pd.DataFrame(all_rows).drop_duplicates("review_id")
    df = df[df["text"].str.len() > 0]
    df.to_csv(config.OUT_PLAYSTORE, index=False)
    print(f"Saved {len(df)} Play Store reviews -> {config.OUT_PLAYSTORE}")
    return df


if __name__ == "__main__":
    fetch_playstore()
