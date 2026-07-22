"""Stage 2 - AI-powered category-discovery analysis.

Takes the targeted candidate corpus produced by build_discovery_sample.py
and tags each feedback item using the controlled category-discovery taxonomy.

Input:
    data/discovery_candidates.csv

Cache:
    data/extracted_discovery_v4.jsonl

Output:
    data/enriched_discovery_v4.csv

Test run:
    python3 extract.py --limit 50

Full run:
    python3 extract.py
"""

import os
import json
import time
import argparse
import pandas as pd
import anthropic
from dotenv import load_dotenv
from taxonomy import EXTRACTION_TOOL, SYSTEM_PROMPT


load_dotenv()
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY


# ---------------------------------------------------------------------
# MODEL + FILES
# ---------------------------------------------------------------------

MODEL = "claude-haiku-4-5-20251001"

INPUT = "data/discovery_candidates.csv"
CACHE = "data/extracted_discovery_final.jsonl"
OUT = "data/enriched_discovery_final.csv"


# ---------------------------------------------------------------------
# CLASSIFICATION
# ---------------------------------------------------------------------

def classify(text, platform):
    content = f"Platform: {platform}\n\nFeedback:\n{text[:2000]}"

    resp = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "tag_feedback"},
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    for block in resp.content:
        if block.type == "tool_use":
            return block.input

    return None


# ---------------------------------------------------------------------
# RESUMABLE CACHE
# ---------------------------------------------------------------------

def load_done():
    done = {}

    if os.path.exists(CACHE):
        with open(CACHE) as f:
            for line in f:
                row = json.loads(line)
                done[row["uid"]] = row

    return done


# ---------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------

def run(limit=None, stratified=None):

    df = pd.read_csv(INPUT)

    done = load_done()

    todo = df[
        ~df["uid"].isin(done)
    ].reset_index(drop=True)

    if stratified:
        todo = (
            todo
            .groupby(
                ["platform", "source"],
                group_keys=False,
            )
            .head(stratified)
            .reset_index(drop=True)
        )

    elif limit:
        todo = todo.head(limit)

    print(
        f"{len(done)} already tagged; "
        f"processing {len(todo)} now "
        f"(model={MODEL})"
    )

    with open(CACHE, "a") as cache:

        for i, row in todo.iterrows():

            try:

                tags = classify(
                    str(row["text"]),
                    row.get("platform"),
                )

                if tags is None:
                    continue

                rec = {
                   "uid": row["uid"],
    "platform": row.get("platform"),
    "source": row["source"],
    "rating": row.get("rating"),
    "text": row["text"],

    # Retrieval metadata
    "retrieval_families": row.get("retrieval_families"),
    "retrieval_stages": row.get("retrieval_stages"),
    "retrieval_priority": row.get("retrieval_priority"),
    "retrieval_terms": row.get("retrieval_terms"),

    # AI classification
    **tags,
                }

                cache.write(
                    json.dumps(
                        rec,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

                cache.flush()

            except Exception as e:

                print(
                    f"  error on {row['uid']}: "
                    f"{e}; backing off"
                )

                time.sleep(5)

            if (i + 1) % 25 == 0:
                print(
                    f"  {i + 1}/{len(todo)}"
                )

    rows = [
        json.loads(line)
        for line in open(CACHE)
    ]

    enriched = pd.DataFrame(rows)

    enriched.to_csv(
        OUT,
        index=False,
    )

    print(
        f"Saved {len(enriched)} tagged items -> {OUT}"
    )


# ---------------------------------------------------------------------
# COMMAND LINE
# ---------------------------------------------------------------------

if __name__ == "__main__":

    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--limit",
        type=int,
        default=None,
    )

    ap.add_argument(
        "--stratified",
        type=int,
        default=None,
        help="tag N items per (platform, source) group",
    )

    args = ap.parse_args()

    run(
        args.limit,
        args.stratified,
    )
