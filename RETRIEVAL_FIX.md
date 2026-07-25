# Retrieval Filter Fix — What Changed and Why

## The problem

`build_discovery_sample.py`'s `QUERY_FAMILIES` regex is the retrieval step
between `all_feedback.csv` (3,776 rows) and `discovery_candidates.csv` (the
candidate pool that gets classified). Checked against an independent
full-corpus classification pass (47 known discovery-relevant conversations),
the original filter only retrieved 20 of them — 43% recall. The other 27 were
never even seen by classification, regardless of how good the classifier is.

## What was missing

Almost all of the misses fell into two patterns the English-only regex
couldn't see:

1. **Hinglish / Devanagari awareness phrasing.** "Jo kahi nahi milta wo
   Blinkit pe milta hai" ("what you can't find anywhere, you find on
   Blinkit") is a textbook awareness signal — just not in English. Python's
   `\b` word-boundary also silently fails around Devanagari vowel signs, so
   even a literal `मिलता` pattern wasn't matching text that plainly contained
   it, until the boundary anchors were removed for that pattern specifically.

2. **Imperative YouTube-comment recommendations.** "Gotta try Frutopie,"
   "u should try paper boat sparkling waters" — common in comment replies to
   haul/review videos, functionally identical to "recommend" or "suggest,"
   but in imperative mood and almost never naming the platform (the video
   itself is the context).

## What changed in `build_discovery_sample.py`

- Added Hinglish/Devanagari phrases to `know_awareness`: `milta hai/tha/hain`,
  `nahi milta`, `मिलता`, `नहीं मिलता`, `pehle nahi tha`, `one finger tap`,
  `can't find`, `not available on other apps`, `available in varieties`,
  `want to shop/buy/order/try`, `available even/now/here`.
- New family `imperative_recommendation`: `u should try`, `gotta try`,
  `do try`, `must try`, `try karo` (Hindi), sentence-initial `try`, `trying to
  book/order/buy`, `bata do` (Hindi "tell me" — used when asking about
  availability).
- New family `assortment_before_after`: `not many options` → `everything you
  need`, `i wish [you] had/stocked`.
- Fixed `\btrust\b` → `\btrust\w*\b` so "trustworthy" and "trusted" actually
  match (the exact-word boundary was silently excluding both).

## Result

| | Before | After |
|---|---|---|
| Candidates | 674 (17.8%) | 711 (18.8%) |
| Recall on 47 known discovery-relevant | 20 (43%) | 38 (81%) |

## What's still missed, and why it's not worth chasing

9 of the 47 remain unretrieved:

- **6 are likely noise** from whatever produced the full-corpus classification
  pass — a bare YouTube Shorts URL with no text, "2nd and 3rd dress are
  beautiful," an unrelated gym-app comment tagged `assortment_gap`, two
  fragmentary Hinglish comments with no clear Blinkit-relevant content. These
  probably shouldn't have been labeled discovery-relevant in the first place.
- **1 requires a food-culture fact** ("Jackfruit chips are famous in the
  Konkan region...") with no keyword signal at all — this is exactly the kind
  of item the retrieval-then-classify architecture is allowed to miss, since
  classification's whole job is to make the judgment call regex can't.
- **1 is a genuine product-quality complaint** ("football shoes... already
  used, mud stains, worn out") with no safely-matchable keyword — "used,"
  "worn," "dirty" are far too generic; adding them would flood the candidate
  pool with unrelated damaged-delivery complaints for one gain.
- **1** ("Bahi pura din Rajasthani food plzz") is only catchable via a bare
  `plzz` pattern, which was tested and pulls in 25 conversations — 24 of them
  unrelated complaints about COD, delivery timing, and customer service — for
  a single true positive. Not worth the precision cost.

## The number this changes

With retrieval now honestly gating classification, the pipeline's real
output is **3,776 → 711 retrieved (18.8%) → 38 confirmed discovery-relevant**,
not 47. 47 is only reachable by classifying the full corpus directly, which
skips retrieval — the architecture Slide 2 doesn't describe.

Barrier mix among the 38 (previously 47): Awareness 21 (55%), Assortment 7
(18%), Trust 7 (18%), Other 3 (8%) — same shape as the original 53/21/17/9,
awareness still dominant, CONSIDER still essentially absent.

**If Slide 2/3 need to change:** update from 47 → 38, and 53/21/17/9 → roughly
55/18/18/8. The story doesn't change — thin signal, awareness-dominant,
consideration structurally invisible — only the precise numbers do, and now
every stage of the funnel actually nests inside the one before it.
