"""Build a targeted category-discovery candidate corpus.

Why this exists:
A broad quick-commerce feedback corpus contains large amounts of generic
feedback about delivery, refunds, support, pricing, and app experience.

The Blinkit PM research question is narrower:
- Why do users stay within familiar categories?
- What prevents category exploration?
- How do users discover unexpected categories?
- What makes users choose another platform?
- What information is needed before trying unfamiliar purchases?
- What situations trigger category expansion?

This script retrieves POTENTIALLY relevant feedback from all_feedback.csv
using transparent keyword/query-family rules.

IMPORTANT:
A match is only a research CANDIDATE.
It is NOT automatically treated as evidence.

Claude performs the subsequent structured classification.
"""

from pathlib import Path
import re
import pandas as pd


# ---------------------------------------------------------------------
# FILES
# ---------------------------------------------------------------------

INPUT = Path("data/all_feedback.csv")
OUTPUT = Path("data/discovery_candidates.csv")


# ---------------------------------------------------------------------
# RESEARCH QUERY FAMILIES
# ---------------------------------------------------------------------

QUERY_FAMILIES = {

    # ---------------------------------------------------------------
    # KNOW
    # Does the user know the platform/category exists?
    # ---------------------------------------------------------------
    "know_awareness": [
        r"\bdidn'?t know\b",
        r"\bdid not know\b",
        r"\bnever knew\b",
        r"\bnever know\b",
        r"\bwasn'?t aware\b",
        r"\bnot aware\b",
        r"\bsurpris(?:e|ed|ing)\b",
        r"\bdidn'?t expect\b",
        r"\bdid not expect\b",
        r"\bunexpected\b",
        r"\bdiscovered\b",
        r"\bfound out\b",
        r"\bjust found\b",
        r"\bthey sell\b",
        r"\bblinkit sells\b",
        r"\bzepto sells\b",
        r"\bbigbasket sells\b",
        r"\bavailable on blinkit\b",
        r"\bavailable on zepto\b",
        # Hinglish / Hindi "you find it here / you can't find it elsewhere" —
        # the same awareness signal as "didn't know they sold this", just
        # phrased in code-switched or Devanagari text. Missing this pattern
        # was the single largest recall gap in the original filter.
        r"\bkahi nahi milta\b",
        r"\bnahi milta (?:tha|hai)\b",
        r"\bmilta (?:hai|tha|hain)\b",
        r"\bmil jata (?:hai|tha)\b",
        # NOTE: no \b around Devanagari — Python's word-boundary detection
        # breaks around Devanagari vowel signs (matras), so anchored
        # patterns silently fail to match script that's plainly there.
        r"मिलता",
        r"नहीं मिलता",
        r"\bpehle nahi tha\b",
        r"\bone finger tap\b",
        r"\bcan'?t find\b",
        r"\bnot available on (?:other|any other) apps?\b",
        r"\bavailable in (?:varieties|variety)\b",
        r"\bwant to (?:shop|buy|order|try)\b",
        r"\bavailable (?:even|now|here)\b",
    ],

    # ---------------------------------------------------------------
    # KNOW / EXPLORE — imperative recommendation language
    # ("try X", "gotta try Y") — extremely common in YouTube comments
    # replying to a haul/review video, and functionally the same
    # discovery signal as "recommend" or "suggest", just imperative
    # mood and almost never naming the platform explicitly (the video
    # itself is the platform context).
    # ---------------------------------------------------------------
    "imperative_recommendation": [
        r"\bu should try\b",
        r"\byou should try\b",
        r"\bgotta try\b",
        r"\bdo try\b",
        r"\bmust try\b",
        r"\btry karo\b",
        r"^try\b",
        r"\btry(?:ing)? to (?:book|order|buy)\b",
        r"\bbata do\b",
    ],

    # ---------------------------------------------------------------
    # KNOW — implicit before/after assortment-breadth comparison
    # ---------------------------------------------------------------
    "assortment_before_after": [
        r"\bnot many options\b",
        r"\beverything you (?:can think of|need)\b",
        r"\bnow (?:it |they )?(?:has|have) everything\b",
        r"\bbefore there (?:was|were)\b",
        r"\bi wish (?:u|you|they)?\s*(?:would have|had|stocked)\b",
    ],

    # ---------------------------------------------------------------
    # CONSIDER — habit / narrow use
    # Does habitual shopping constrain category breadth?
    # ---------------------------------------------------------------
    "consider_habit": [
        r"\balways (?:buy|order|use|get)\b",
        r"\busually (?:buy|order|use|get)\b",
        r"\bonly (?:buy|order|use|get)\b",
        r"\bonly use\b",
        r"\bonly order\b",
        r"\bsame (?:things|items|products)\b",
        r"\bevery ?day\b",
        r"\bdaily\b",
        r"\bweekly\b",
        r"\bevery week\b",
        r"\broutine\b",
        r"\bregularly\b",
        r"\bregular order\b",
        r"\bregular customer\b",
        r"\bmy groceries\b",
        r"\bfor groceries\b",
        r"\bgrocery shopping\b",
        r"\bmonthly groceries\b",
        r"\bweekly groceries\b",
    ],

    # ---------------------------------------------------------------
    # CONSIDER — alternative destination / mental availability
    # ---------------------------------------------------------------
    "consider_platform_choice": [
        r"\bamazon\b",
        r"\bflipkart\b",
        r"\bnykaa\b",
        r"\bmyntra\b",
        r"\bmeesho\b",
        r"\boffline store\b",
        r"\blocal store\b",
        r"\blocal shop\b",
        r"\bsupermarket\b",
        r"\bbetter than blinkit\b",
        r"\bbetter than zepto\b",
        r"\binstead of blinkit\b",
        r"\binstead of zepto\b",
        r"\brather (?:buy|order)\b",
        r"\bprefer (?:amazon|flipkart|nykaa|myntra|offline)\b",
    ],

    # ---------------------------------------------------------------
    # CONFIDENCE — decision support
    # ---------------------------------------------------------------
    "confidence_information": [
        r"\breviews?\b",
        r"\bratings?\b",
        r"\bcompare\b",
        r"\bcomparison\b",
        r"\bspecifications?\b",
        r"\bspecs\b",
        r"\bcompatible\b",
        r"\bcompatibility\b",
        r"\bsuitable\b",
        r"\bsuitability\b",
        r"\bwhich one\b",
        r"\bwhich product\b",
        r"\bwhich brand\b",
        r"\bhow do i know\b",
        r"\bdetails\b",
        r"\bproduct information\b",
        r"\bdescription\b",
        r"\bsize chart\b",
        r"\bingredients?\b",
    ],

    # ---------------------------------------------------------------
    # CONFIDENCE — authenticity / quality / purchase risk
    # ---------------------------------------------------------------
    "confidence_trust": [
        r"\bgenuine\b",
        r"\boriginal\b",
        r"\bfake\b",
        r"\bauthentic\b",
        r"\bauthenticity\b",
        r"\bcounterfeit\b",
        r"\btrust\w*\b",
        r"\bquality\b",
        r"\bwarranty\b",
        r"\bguarantee\b",
        r"\breturn policy\b",
        r"\breturnable\b",
        r"\breplacement\b",
        r"\bsealed\b",
        r"\bexpired\b",
        r"\bexpiry\b",
    ],

    # ---------------------------------------------------------------
    # HIGHER-CONSIDERATION / EXPANSION CATEGORIES
    #
    # Category mentions are NOT evidence by themselves.
    # They are retrieval signals that help us locate potentially
    # relevant conversations.
    # ---------------------------------------------------------------
    "expansion_category": [
        r"\belectronics?\b",
        r"\bheadphones?\b",
        r"\bearphones?\b",
        r"\bcharger\b",
        r"\bcable\b",
        r"\bpower bank\b",
        r"\bkeyboard\b",
        r"\bmouse\b",
        r"\bsmartwatch\b",
        r"\bwatch\b",
        r"\bskincare\b",
        r"\bskin care\b",
        r"\bmakeup\b",
        r"\bcosmetics?\b",
        r"\bbeauty\b",
        r"\bserum\b",
        r"\bsunscreen\b",
        r"\bfashion\b",
        r"\bclothes\b",
        r"\bclothing\b",
        r"\bapparel\b",
        r"\bhome decor\b",
        r"\bhome décor\b",
        r"\bbedsheets?\b",
        r"\bbed sheets?\b",
        r"\bpillow\b",
        r"\bkitchenware\b",
        r"\bappliances?\b",
        r"\bpet supplies\b",
        r"\bpet food\b",
        r"\bdog food\b",
        r"\bcat food\b",
        r"\bbaby products?\b",
        r"\bdiapers?\b",
        r"\btoys?\b",
        r"\bstationery\b",
        r"\bprintouts?\b",
        r"\bprint(?:ing)? service\b",
    ],

    # ---------------------------------------------------------------
    # CONTEXT — urgency
    # ---------------------------------------------------------------
    "context_urgency": [
        r"\burgent\b",
        r"\burgently\b",
        r"\bemergency\b",
        r"\bneeded (?:it )?(?:now|immediately|urgently)\b",
        r"\bneed (?:it )?(?:now|immediately|urgently)\b",
        r"\blast minute\b",
        r"\bright now\b",
        r"\bwithin minutes\b",
        r"\bquickly needed\b",
        r"\bforgot to buy\b",
        r"\bran out\b",
        r"\brun out\b",
    ],

    # ---------------------------------------------------------------
    # CONTEXT — occasions / life events
    # ---------------------------------------------------------------
    "context_life_event": [
        r"\bbirthday\b",
        r"\bparty\b",
        r"\bguests?\b",
        r"\bfestival\b",
        r"\bdiwali\b",
        r"\bholi\b",
        r"\bcelebration\b",
        r"\bgift\b",
        r"\bgifting\b",
        r"\bnew baby\b",
        r"\bbaby shower\b",
        r"\bnewborn\b",
        r"\bnew pet\b",
        r"\bpuppy\b",
        r"\bkitten\b",
        r"\bmoving\b",
        r"\bmoved (?:house|home|apartment)\b",
        r"\bnew house\b",
        r"\bnew apartment\b",
        r"\btravel\b",
        r"\btrip\b",
    ],

    # ---------------------------------------------------------------
    # DISCOVERY / EXPLORATION LANGUAGE
    # ---------------------------------------------------------------
    "exploration_behavior": [
        r"\bbrows(?:e|ed|ing)\b",
        r"\bexplor(?:e|ed|ing)\b",
        r"\bdiscover(?:ed|ing)?\b",
        r"\brecommend(?:ed|ation|ations)?\b",
        r"\bsuggest(?:ed|ion|ions)?\b",
        r"\btried for the first time\b",
        r"\bfirst time (?:buying|ordering|trying)\b",
        r"\bdecided to try\b",
        r"\bwill try\b",
        r"\bwant to try\b",
        r"\bimpulse\b",
        r"\bimpulsive\b",
    ],
}


# ---------------------------------------------------------------------
# COMPILE REGEX ONCE
# ---------------------------------------------------------------------

COMPILED = {
    family: [re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns]
    for family, patterns in QUERY_FAMILIES.items()
}


# ---------------------------------------------------------------------
# MATCHING
# ---------------------------------------------------------------------

def match_families(text):
    """Return query families and matched snippets/patterns for one text."""

    if pd.isna(text):
        return [], []

    text = str(text)

    matched_families = []
    matched_terms = []

    for family, patterns in COMPILED.items():

        family_matches = []

        for pattern in patterns:
            match = pattern.search(text)

            if match:
                family_matches.append(match.group(0))

        if family_matches:
            matched_families.append(family)
            matched_terms.extend(family_matches)

    # Remove duplicates while preserving order
    matched_terms = list(dict.fromkeys(matched_terms))

    return matched_families, matched_terms


def research_stage(families):
    """Map retrieval families into the PM research framework."""

    stages = []

    if "know_awareness" in families:
        stages.append("KNOW")

    if (
        "consider_habit" in families
        or "consider_platform_choice" in families
    ):
        stages.append("CONSIDER")

    if (
        "confidence_information" in families
        or "confidence_trust" in families
    ):
        stages.append("CONFIDENCE")

    if (
        "context_urgency" in families
        or "context_life_event" in families
    ):
        stages.append("CONTEXT")

    if "exploration_behavior" in families:
        stages.append("EXPLORE")

    if "expansion_category" in families:
        stages.append("CATEGORY")

    return stages


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"{INPUT} does not exist.\n"
            "Run: python3 combine.py\n"
            "before building the discovery candidate sample."
        )

    df = pd.read_csv(INPUT)

    if "text" not in df.columns:
        raise ValueError(
            "all_feedback.csv must contain a 'text' column."
        )

    print(f"Loaded {len(df):,} rows from {INPUT}")

    results = df["text"].apply(match_families)

    df["retrieval_families"] = results.apply(
        lambda x: "|".join(x[0])
    )

    df["retrieval_terms"] = results.apply(
        lambda x: "|".join(x[1])
    )

    df["retrieval_stages"] = results.apply(
        lambda x: "|".join(research_stage(x[0]))
    )

    df["retrieval_family_count"] = results.apply(
        lambda x: len(x[0])
    )

    # -------------------------------------------------------------
    # CANDIDATE RULE
    # -------------------------------------------------------------
    #
    # Include anything matching at least one targeted query family.
    #
    # This deliberately favors recall at the retrieval stage.
    # Claude + human evaluation will provide precision later.
    #
    candidates = df[
        df["retrieval_family_count"] >= 1
    ].copy()

    # Prioritize richer signals without excluding single-family matches.
    candidates["retrieval_priority"] = candidates[
        "retrieval_family_count"
    ].apply(
        lambda n: "high" if n >= 3 else "medium" if n == 2 else "standard"
    )

    # Deduplicate again for safety.
    candidates = candidates.drop_duplicates(
        subset=["text"],
        keep="first",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    candidates.to_csv(
        OUTPUT,
        index=False,
    )

    # -------------------------------------------------------------
    # REPORT
    # -------------------------------------------------------------

    print("\n" + "=" * 65)
    print("DISCOVERY RETRIEVAL REPORT")
    print("=" * 65)

    print(
        f"\nBroad corpus:              {len(df):,}"
    )

    print(
        f"Discovery candidates:      {len(candidates):,}"
    )

    if len(df):
        print(
            f"Candidate retrieval rate:  "
            f"{len(candidates) / len(df):.1%}"
        )

    print("\nCandidate priority:")
    print(
        candidates["retrieval_priority"]
        .value_counts()
        .to_string()
    )

    print("\nQuery-family matches:")

    family_counts = {}

    for families in candidates["retrieval_families"]:
        for family in str(families).split("|"):
            if family:
                family_counts[family] = (
                    family_counts.get(family, 0) + 1
                )

    for family, count in sorted(
        family_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"  {family:<30} {count:>5}")

    print("\nResearch-stage matches:")

    stage_counts = {}

    for stages in candidates["retrieval_stages"]:
        for stage in str(stages).split("|"):
            if stage:
                stage_counts[stage] = (
                    stage_counts.get(stage, 0) + 1
                )

    for stage, count in sorted(
        stage_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"  {stage:<15} {count:>5}")

    if "platform" in candidates.columns:
        print("\nCandidates by platform:")
        print(
            candidates["platform"]
            .value_counts()
            .to_string()
        )

    if "source" in candidates.columns:
        print("\nCandidates by source:")
        print(
            candidates["source"]
            .value_counts()
            .to_string()
        )

    print(
        f"\nSaved -> {OUTPUT}"
    )

    print("\nIMPORTANT:")
    print(
        "These are retrieval CANDIDATES, not validated discovery insights."
    )
    print(
        "Claude and human evaluation should determine which records "
        "actually provide discovery evidence."
    )


if __name__ == "__main__":
    main()
