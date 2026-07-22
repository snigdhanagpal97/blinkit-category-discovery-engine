"""Merge every source into one unified all_feedback.csv (with a platform tag)."""
import os
import pandas as pd
import config


def _load(path, default_platform=None):
    if not os.path.exists(path):
        print(f"  skip (missing): {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    id_col = next((c for c in ["review_id", "post_id", "video_id"] if c in df.columns), None)
    ids = df[id_col].astype(str) if id_col else df.index.astype(str)
    platform = df["platform"] if "platform" in df.columns else default_platform
    out = pd.DataFrame({
        "uid": df["source"].astype(str) + "_" + ids + "_" + df.index.astype(str),
        "platform": platform,
        "source": df["source"].astype(str),
        "text": df["text"].astype(str),
        "rating": df["rating"] if "rating" in df.columns else pd.NA,
        "date": df["date"] if "date" in df.columns else pd.NA,
    })
    return out


def combine():
    frames = [
        _load(config.OUT_PLAYSTORE, "blinkit"),
        _load(config.OUT_APPSTORE, "blinkit"),
        _load(config.OUT_REDDIT, "blinkit"),
        _load(config.OUT_COMPETITORS),   # platform comes from the file
        _load(config.OUT_YOUTUBE),       # platform comes from the file
    ]
    df = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    df["text"] = df["text"].str.strip()
    df = df[df["text"].str.len() > 10].drop_duplicates("text").reset_index(drop=True)
    df.to_csv(config.OUT_COMBINED, index=False)
    print(f"Combined {len(df)} feedback items -> {config.OUT_COMBINED}")
    print(df.groupby(["platform", "source"]).size().to_string())
    return df


if __name__ == "__main__":
    combine()
