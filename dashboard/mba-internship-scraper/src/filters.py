"""Job filtering helpers for MBA internship search."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from html import unescape
from typing import Any

MBA_KEYWORDS = re.compile(
    r"\b(mba|business\s+school|graduate\s+student|"
    r"mba\s+intern(?:ship)?|summer\s+associate|"
    r"associate\s+consultant|consulting\s+intern)\b",
    re.IGNORECASE,
)

INTERNSHIP_LEVEL_KEYWORDS = re.compile(
    r"\b(intern(?:ship)?|apprentice(?:ship)?|co-?op|"
    r"summer\s+associate|mba\s+intern)\b",
    re.IGNORECASE,
)

ROLE_TYPE_KEYWORDS = {
    "product": re.compile(
        r"\b(?:product(?:\s+management|\s+manager|\s+strategy|\s+analyst)?|"
        r"pm|product\s+marketing)\b",
        re.IGNORECASE,
    ),
    "strategy": re.compile(
        r"\b(strategy|strategic|corporate\s+development|bizops|business\s+operations)\b",
        re.IGNORECASE,
    ),
    "growth": re.compile(
        r"\b(growth|activation|acquisition|lifecycle|demand\s+gen)\b",
        re.IGNORECASE,
    ),
    "operations": re.compile(
        r"\b(operations|ops|supply\s+chain|program\s+management)\b",
        re.IGNORECASE,
    ),
}

NON_US_LOCATION_KEYWORDS = re.compile(
    r"\b("
    r"canada|toronto|vancouver|montreal|"
    r"united\s+kingdom|london|uk\b|"
    r"india|bangalore|bengaluru|mumbai|delhi|hyderabad|"
    r"germany|berlin|munich|france|paris|"
    r"ireland|dublin|"
    r"australia|sydney|melbourne|"
    r"singapore|japan|tokyo|"
    r"brazil|mexico|"
    r"emea|apac|latam|"
    r"remote\s*[-–—]?\s*(?:global|worldwide|anywhere)"
    r")\b",
    re.IGNORECASE,
)

US_LOCATION_KEYWORDS = re.compile(
    r"(?:"
    r"united\s+states|\bus\b|\busa\b|"
    r"remote.*\b(?:us|usa|united\s+states)\b|"
    r"\b(?:us|usa)\b.*remote|"
    r",\s*[A-Z]{2}\b|"
    r"alabama|alaska|arizona|arkansas|california|colorado|connecticut|"
    r"delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|"
    r"kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|"
    r"minnesota|mississippi|missouri|montana|nebraska|nevada|"
    r"new\s+hampshire|new\s+jersey|new\s+mexico|new\s+york|"
    r"north\s+carolina|north\s+dakota|ohio|oklahoma|oregon|"
    r"pennsylvania|rhode\s+island|south\s+carolina|south\s+dakota|"
    r"tennessee|texas|utah|vermont|virginia|washington|"
    r"west\s+virginia|wisconsin|wyoming|"
    r"san\s+francisco|seattle|austin|boston|chicago|denver|"
    r"los\s+angeles|new\s+york\s+city|nyc|atlanta|miami|"
    r"raleigh|durham|charlotte|san\s+diego|portland|"
    r"palo\s+alto|mountain\s+view|menlo\s+park|"
    r"santa\s+clara|cupertino|redmond|cambridge"
    r")",
    re.IGNORECASE,
)

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = HTML_TAG_RE.sub(" ", unescape(value))
    return WHITESPACE_RE.sub(" ", text).strip()


def job_text_blob(job: dict[str, Any]) -> str:
    parts = [
        job.get("title", ""),
        job.get("location", {}).get("name", ""),
        strip_html(job.get("content", "")),
    ]
    for office in job.get("offices", []) or []:
        parts.append(office.get("name", ""))
        parts.append(office.get("location", "") or "")
    for department in job.get("departments", []) or []:
        parts.append(department.get("name", ""))
    metadata = job.get("metadata")
    if metadata:
        parts.append(str(metadata))
    return " ".join(parts)


def parse_updated_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def is_recently_posted(job: dict[str, Any], max_days: int) -> bool:
    updated_at = parse_updated_at(job.get("updated_at"))
    if updated_at is None:
        return False
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    return updated_at >= cutoff


def is_us_location(job: dict[str, Any]) -> bool:
    location_name = job.get("location", {}).get("name", "")
    office_locations = [
        office.get("location") or office.get("name", "")
        for office in (job.get("offices") or [])
    ]
    combined = " | ".join([location_name, *office_locations])

    if NON_US_LOCATION_KEYWORDS.search(combined):
        return False

    if US_LOCATION_KEYWORDS.search(combined):
        return True

    # Ambiguous remote with no country — assume US for tech MBA boards
    if re.search(r"\bremote\b", combined, re.IGNORECASE):
        return True

    return False


def is_internship_level(text: str) -> bool:
    return bool(INTERNSHIP_LEVEL_KEYWORDS.search(text))


def is_mba_role(text: str) -> bool:
    return bool(MBA_KEYWORDS.search(text))


def detect_role_types(text: str) -> list[str]:
    matched: list[str] = []
    for role_type, pattern in ROLE_TYPE_KEYWORDS.items():
        if pattern.search(text):
            matched.append(role_type)
    return matched


def extract_requirements_snippet(text: str, max_length: int = 280) -> str:
    clean = strip_html(text)
    if not clean:
        return "No description available."

    lowered = clean.lower()
    markers = [
        "qualifications",
        "requirements",
        "what you'll bring",
        "what you will bring",
        "what we're looking for",
        "who you are",
        "about you",
    ]
    start = 0
    for marker in markers:
        idx = lowered.find(marker)
        if idx != -1:
            start = idx
            break

    snippet = clean[start : start + max_length].strip()
    if len(clean) > start + max_length:
        snippet += "..."
    return snippet


def passes_hard_filters(job: dict[str, Any], *, max_days_since_posted: int) -> tuple[bool, str]:
    text = job_text_blob(job)
    title = job.get("title", "")

    if not is_recently_posted(job, max_days_since_posted):
        return False, "posted_outside_window"

    if not is_us_location(job):
        return False, "non_us_location"

    if not is_internship_level(f"{title} {text}"):
        return False, "not_internship_level"

    if not is_mba_role(text):
        return False, "not_mba_role"

    role_types = detect_role_types(f"{title} {text}")
    if not role_types:
        return False, "role_type_mismatch"

    return True, "matched"
