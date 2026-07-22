import pandas as pd
from pathlib import Path

INPUT = Path("data/enriched_discovery_final.csv")
OUTPUT = Path("data/dashboard_data.csv")

df = pd.read_csv(INPUT)

# Fields useful for the public research explorer
KEEP_COLUMNS = [
    "uid",
    "platform",
    "source",
    "rating",
    "text",
    "discovery_relevant",
    "primary_theme",
    "new_category_barrier",
    "purchase_trigger",
    "consideration_level",
    "categories_mentioned",
    "jtbd",
    "external_platform",
    "segment_signal",
    "sentiment",
    "confidence",
]

# Only keep columns that actually exist
columns = [c for c in KEEP_COLUMNS if c in df.columns]

dashboard = df[columns].copy()

# Remove exact duplicate feedback
if "text" in dashboard.columns:
    dashboard = dashboard.drop_duplicates(subset=["text"])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
dashboard.to_csv(OUTPUT, index=False)

print(f"Saved {len(dashboard):,} dashboard records -> {OUTPUT}")
print(f"Columns: {list(dashboard.columns)}")
