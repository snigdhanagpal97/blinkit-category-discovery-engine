"""Resume-aware job scoring and filtering for MBA Summer 2027 internships."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Any

from scrapers.base import NormalizedJob

ROOT = Path(__file__).resolve().parent
DEFAULT_RESUME_PATH = ROOT / "my_resume.md"

# --- Hard filter patterns ---

SUMMER_2027 = re.compile(
    r"\b(summer\s+2027|2027\s+summer|intern(?:ship)?\s+2027|2027\s+intern)\b",
    re.IGNORECASE,
)

MBA_OR_LEVEL = re.compile(
    r"\b(mba|business\s+school|graduate\s+student|"
    r"mba\s+intern(?:ship)?|summer\s+associate|"
    r"associate\s+consultant|consulting\s+intern|"
    r"associate|analyst)\b",
    re.IGNORECASE,
)

INTERNSHIP_LEVEL = re.compile(
    r"\b(intern(?:ship)?|apprentice(?:ship)?|co-?op|"
    r"summer\s+associate|mba\s+intern)\b",
    re.IGNORECASE,
)

ROLE_KEYWORDS = re.compile(
    r"\b(product|strategy|growth|operations|pm|"
    r"product\s+manager|product\s+management|"
    r"business\s+operations|bizops)\b",
    re.IGNORECASE,
)

NON_US = re.compile(
    r"\b(canada|toronto|vancouver|united\s+kingdom|london|uk\b|"
    r"india|bangalore|mumbai|germany|france|paris|ireland|dublin|"
    r"australia|singapore|japan|tokyo|brazil|mexico|emea|apac|latam)\b",
    re.IGNORECASE,
)

US_LOCATIONS = re.compile(
    r"(?:united\s+states|\bus\b|\busa\b|"
    r"california|new\s+york|texas|washington|massachusetts|"
    r"san\s+francisco|mountain\s+view|palo\s+alto|menlo\s+park|"
    r"seattle|boston|nyc|new\s+york\s+city|chicago|austin|"
    r"cupertino|redmond|cambridge|raleigh|durham|charlotte|"
    r"remote.*\b(?:us|usa|united\s+states)\b|"
    r",\s*[A-Z]{2}\b)",
    re.IGNORECASE,
)

PREFERRED_LOCATIONS = re.compile(
    r"\b(san\s+francisco|sf\b|mountain\s+view|palo\s+alto|"
    r"menlo\s+park|new\s+york|nyc|seattle|boston|"
    r"cupertino|redmond|cambridge)\b",
    re.IGNORECASE,
)

HTML_TAG = re.compile(r"<[^>]+>")
WHITESPACE = re.compile(r"\s+")

# --- Scoring patterns ---

MBA_PM_STRATEGY = re.compile(
    r"\b(mba.*(?:product|strategy|growth|pm|operations)|"
    r"(?:product|strategy|growth|pm|operations).*mba)\b",
    re.IGNORECASE,
)

PRODUCT_ANALYTICS = re.compile(
    r"\b(product\s+analytics|analytics|data-driven|sql|python|"
    r"experimentation|a/b\s+test|forecasting|metrics|quantitative)\b",
    re.IGNORECASE,
)

AI_ML = re.compile(
    r"\b(ai|artificial\s+intelligence|machine\s+learning|ml|"
    r"llm|generative\s+ai|automation|ai\s+product)\b",
    re.IGNORECASE,
)

# Resume-specific boosts
RESUME_PATTERNS: dict[str, re.Pattern[str]] = {
    "quick_commerce": re.compile(
        r"\b(quick\s*commerce|grocery|delivery|marketplace|e-?commerce|"
        r"on-?demand|last\s+mile|fulfillment)\b",
        re.IGNORECASE,
    ),
    "pricing_forecasting": re.compile(
        r"\b(dynamic\s+pricing|pricing|demand\s+forecasting|forecasting|"
        r"supply\s+chain|inventory)\b",
        re.IGNORECASE,
    ),
    "data_skills": re.compile(
        r"\b(data-driven|sql|python|automation|analytics|experimentation)\b",
        re.IGNORECASE,
    ),
    "target_roles": re.compile(
        r"\b(ai\s+product|strategy|growth|operations|product\s+management)\b",
        re.IGNORECASE,
    ),
}


@dataclass
class MatchResult:
    score: int
    reasons: list[str] = field(default_factory=list)
    role_types: list[str] = field(default_factory=list)
    breakdown: dict[str, int] = field(default_factory=dict)


@dataclass
class ResumeProfile:
    text: str
    keywords: list[str] = field(default_factory=list)


def load_resume(path: Path = DEFAULT_RESUME_PATH) -> ResumeProfile:
    if not path.exists():
        return ResumeProfile(text="", keywords=[])
    text = path.read_text(encoding="utf-8")
    keywords = [
        "quick-commerce",
        "product analytics",
        "dynamic pricing",
        "demand forecasting",
        "sql",
        "python",
        "ai product",
        "strategy",
        "growth",
        "operations",
        "blinkit",
        "noon",
        "d2c",
        "experimentation",
    ]
    return ResumeProfile(text=text.lower(), keywords=keywords)


def strip_html(value: str) -> str:
    if not value:
        return ""
    text = HTML_TAG.sub(" ", unescape(value))
    return WHITESPACE.sub(" ", text).strip()


def job_blob(job: NormalizedJob) -> str:
    return " ".join(
        [
            job.title,
            job.location,
            strip_html(job.content),
        ]
    )


def is_us_location(job: NormalizedJob) -> bool:
    combined = job.location
    if NON_US.search(combined):
        return False
    if US_LOCATIONS.search(combined):
        return True
    if re.search(r"\bremote\b", combined, re.IGNORECASE):
        return True
    return job.location.lower() in ("unknown", "")


def is_recent(job: NormalizedJob, max_days: int) -> bool:
    if not job.updated_at:
        return True  # custom scrapers may lack dates; don't exclude
    try:
        normalized = job.updated_at.replace("Z", "+00:00")
        updated = datetime.fromisoformat(normalized)
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
        return updated >= cutoff
    except ValueError:
        return True


def passes_hard_filters(
    job: NormalizedJob,
    *,
    max_days: int,
    hiring_mba: bool,
    require_summer_2027: bool = True,
) -> tuple[bool, str]:
    blob = job_blob(job)
    title_blob = f"{job.title} {blob}"

    if not is_recent(job, max_days):
        return False, "posted_outside_window"

    if not is_us_location(job):
        return False, "non_us_location"

    if not INTERNSHIP_LEVEL.search(title_blob):
        return False, "not_internship_level"

    if hiring_mba and not MBA_OR_LEVEL.search(title_blob):
        return False, "not_mba_or_associate_level"

    if not ROLE_KEYWORDS.search(title_blob):
        return False, "role_keyword_mismatch"

    if require_summer_2027 and not SUMMER_2027.search(title_blob):
        # Allow if title clearly says MBA intern without year (early postings)
        if not re.search(r"\b(mba\s+intern|summer\s+associate)\b", title_blob, re.I):
            return False, "not_summer_2027"

    return True, "matched"


def detect_role_types(text: str) -> list[str]:
    types: list[str] = []
    for name, pattern in [
        ("product", re.compile(r"\b(product|pm)\b", re.I)),
        ("strategy", re.compile(r"\b(strategy|bizops)\b", re.I)),
        ("growth", re.compile(r"\bgrowth\b", re.I)),
        ("operations", re.compile(r"\b(operations|ops)\b", re.I)),
    ]:
        if pattern.search(text):
            types.append(name)
    return types


def score_job(job: NormalizedJob, resume: ResumeProfile) -> MatchResult:
    blob = job_blob(job)
    title_blob = f"{job.title} {blob}"
    role_types = detect_role_types(title_blob)

    breakdown: dict[str, int] = {}
    reasons: list[str] = []

    # MBA + PM/Strategy/Growth (+4)
    mba_pm = 0
    if MBA_PM_STRATEGY.search(title_blob) or (
        re.search(r"\bmba\b", title_blob, re.I)
        and role_types
    ):
        mba_pm = 4
        reasons.append("MBA + product/strategy/growth role alignment")
    elif re.search(r"\b(mba|associate|analyst)\b", title_blob, re.I) and role_types:
        mba_pm = 2
        reasons.append("MBA-friendly associate/analyst role with target function")
    breakdown["mba_pm_strategy"] = mba_pm

    # Product analytics/data (+2)
    analytics = 2 if PRODUCT_ANALYTICS.search(title_blob) else 0
    if analytics:
        reasons.append("Product analytics/data emphasis matches SQL/Python background")
    breakdown["product_analytics"] = analytics

    # AI/ML (+2)
    ai_pts = 2 if AI_ML.search(title_blob) else 0
    if ai_pts:
        reasons.append("AI/ML component aligns with AI PM focus at Kenan-Flagler")
    breakdown["ai_ml"] = ai_pts

    # Location preference (+1)
    loc_pts = 1 if PREFERRED_LOCATIONS.search(job.location) else 0
    if loc_pts:
        reasons.append("Preferred location (SF/NYC/Seattle/Boston)")
    breakdown["location"] = loc_pts

    # Company tier (+1 for tier 1-2)
    tier_pts = 1 if job.tier <= 2 else 0
    if tier_pts:
        reasons.append(f"Top-tier company (tier {job.tier})")
    breakdown["company_tier"] = tier_pts

    # Resume boosts (up to +2 total)
    resume_boost = 0
    for label, pattern in RESUME_PATTERNS.items():
        if pattern.search(title_blob):
            resume_boost += 1
            if label == "quick_commerce":
                reasons.append("Quick-commerce/marketplace fit (Blinkit/Noon experience)")
            elif label == "pricing_forecasting":
                reasons.append("Pricing/forecasting fit (dynamic pricing + demand forecasting)")
            elif label == "data_skills":
                reasons.append("Data-driven role matches SQL/Python + experimentation skills")
            elif label == "target_roles":
                reasons.append("Matches target AI PM / strategy / growth path")

    resume_boost = min(2, resume_boost)
    breakdown["resume_boost"] = resume_boost

    raw_total = mba_pm + analytics + ai_pts + loc_pts + tier_pts + resume_boost
    score = min(10, raw_total)

    if role_types:
        reasons.append(f"Role types: {', '.join(role_types)}")

    return MatchResult(
        score=score,
        reasons=reasons,
        role_types=role_types,
        breakdown=breakdown,
    )


def format_match(job: NormalizedJob, result: MatchResult) -> dict[str, Any]:
    content = strip_html(job.content)
    snippet = content[:280] + ("..." if len(content) > 280 else "") if content else "No description."

    return {
        "company": job.company,
        "title": job.title,
        "score": result.score,
        "score_breakdown": result.breakdown,
        "role_types": result.role_types,
        "location": job.location,
        "url": job.url,
        "updated_at": job.updated_at or "",
        "requirements_snippet": snippet,
        "match_reasons": result.reasons,
        "job_id": job.id,
        "dedupe_key": job.dedupe_key(),
        "ats": job.ats,
    }
