# Blinkit Flash · Discovery Analytics

A dark analytics dashboard over 3,776 public review conversations, with your
50-row human-labelled set as a separate drill-down layer. Data is baked in —
no upload step, it renders on load.

## Install

Unzip into the root of `blinkit-category-discovery-engine`, overwriting when asked.

```bash
cd ~/Downloads/blinkit-engine        # wherever the repo lives
cp -R ~/Downloads/blinkit-dashboard/. .

npm install
npm run dev                          # http://localhost:3000
```

`/` redirects to `/dashboard`, so the root no longer 404s.

## Ship it

```bash
git add app public package.json tsconfig.json next.config.js vercel.json
git commit -m "Discovery analytics dashboard"
git push origin main
```

Vercel rebuilds on push. If the build still tries to run `app.py` as a Python
function, add this to `.vercelignore` at the repo root:

```
app.py
*.py
requirements.txt
```

## What's in it

| Tab | What it answers |
|-----|-----------------|
| Overview | Theme mix, sentiment split, volume over time, non-grocery categories customers raise |
| Insights | All 3,776 conversations — filter by platform, barrier, sentiment, source; search the text |
| Discovery | The 108 discovery-relevant conversations, isolated |
| Competitive | Trust complaints and barrier mix across Blinkit, Zepto, BigBasket |
| Golden set | The 50 hand-labelled rows, click any card for the full taxonomy and the labelling rationale |

The KNOW / CONSIDER / CONFIDENCE rail sits above every tab — it's the same
framing as the deck, so the dashboard and the slides argue the same thing.

## Refreshing the data

`public/data.json` is generated from your two CSVs. Re-run the prep script when
you scrape new reviews and replace the file — nothing else changes.

## Honesty note for the deck

Themes across the full 3,776 come from a keyword taxonomy, not an LLM pass.
The 50-row golden set is human-labelled. The footer says so, and you should
too if anyone asks how the numbers were produced.
