"""Match scoring for MBA internship roles."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .filters import detect_role_types, job_text_blob, strip_html

PRODUCT_EXPERIENCE = re.compile(
    r"\b(product\s+(?:management|manager|strategy|analytics|ops)|"
    r"product-minded|0\s*[-→>]+\s*1|roadmap|user\s+research|"
    r"cross-functional|product\s+launch)\b",
    re.IGNORECASE,
)

ANALYTICS_DATA = re.compile(
    r"\b(analytics|analytical|data-driven|sql|python|"
    r"experimentation|a/b\s+test|metrics|forecasting|"
    r"business\s+intelligence|quantitative|statistics)\b",
    re.IGNORECASE,
)

AI_ML = re.compile(
    r"\b(ai|artificial\s+intelligence|machine\s+learning|ml|"
    r"llm|generative\s+ai|deep\s+learning|nlp|"
    r"ai\s+product|ai\s+strategy)\b",
    re.IGNORECASE,
)

MBA_STRONG = re.compile(
    r"\b(mba\s+intern(?:ship)?|mba\s+candidate|currently\s+enrolled\s+in\s+.*mba|"
    r"business\s+school\s+student|returning\s+to\s+.*mba)\b",
    re.IGNORECASE,
)


@dataclass
class MatchScore:
    total: int
    product_experience: int
    analytics_data: int
    ai_ml: int
    mba_hiring: int
    role_fit: int
    role_types: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return "; ".join(self.reasons)


def score_job(job: dict[str, Any]) -> MatchScore:
    text = job_text_blob(job)
    title = job.get("title", "")
    combined = f"{title} {text}"

    role_types = detect_role_types(combined)

    product_pts = 3 if PRODUCT_EXPERIENCE.search(combined) else (
        2 if "product" in role_types else 0
    )
    analytics_pts = 3 if ANALYTICS_DATA.search(combined) else 1
    ai_pts = 2 if AI_ML.search(combined) else 0

    if MBA_STRONG.search(combined):
        mba_pts = 2
    else:
        mba_pts = 1

    role_fit_pts = min(2, len(role_types))

    total = min(10, product_pts + analytics_pts + ai_pts + mba_pts + role_fit_pts)

    reasons: list[str] = []
    if product_pts >= 2:
        reasons.append("Strong product experience fit (5 yrs Blinkit/Noon + D2C founder)")
    if analytics_pts >= 2:
        reasons.append("Analytics/data emphasis matches your SQL/Python + experimentation background")
    if ai_pts:
        reasons.append("AI/ML component aligns with your AI product management focus at Kenan-Flagler")
    if mba_pts == 2:
        reasons.append("Explicitly targets MBA candidates")
    else:
        reasons.append("MBA-friendly internship language detected")
    if role_types:
        reasons.append(f"Role type match: {', '.join(role_types)}")

    return MatchScore(
        total=total,
        product_experience=product_pts,
        analytics_data=analytics_pts,
        ai_ml=ai_pts,
        mba_hiring=mba_pts,
        role_fit=role_fit_pts,
        role_types=role_types,
        reasons=reasons,
    )


def format_match_result(job: dict[str, Any], company_name: str, score: MatchScore) -> dict[str, Any]:
    from .filters import extract_requirements_snippet

    content = strip_html(job.get("content", ""))
    return {
        "company": company_name,
        "title": job.get("title", ""),
        "score": score.total,
        "score_breakdown": {
            "product_experience": score.product_experience,
            "analytics_data": score.analytics_data,
            "ai_ml": score.ai_ml,
            "mba_hiring": score.mba_hiring,
            "role_fit": score.role_fit,
        },
        "role_types": score.role_types,
        "location": job.get("location", {}).get("name", "Unknown"),
        "url": job.get("absolute_url", ""),
        "updated_at": job.get("updated_at", ""),
        "requirements_snippet": extract_requirements_snippet(content),
        "match_reasons": score.reasons,
        "job_id": str(job.get("id", "")),
    }
