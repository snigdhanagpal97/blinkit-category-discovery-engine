"""Unit tests for resume matching and filters."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from resume_matcher import (  # noqa: E402
    ResumeProfile,
    passes_hard_filters,
    score_job,
)
from scrapers.base import NormalizedJob  # noqa: E402


def _job(**kwargs) -> NormalizedJob:
    defaults = {
        "id": "123",
        "title": "MBA Product Management Intern - Summer 2027",
        "location": "San Francisco, CA",
        "url": "https://example.com/job/123",
        "content": (
            "We are seeking an MBA intern for Summer 2027. "
            "Product strategy, SQL, Python, AI/ML experience preferred. "
            "Dynamic pricing and analytics background a plus."
        ),
        "updated_at": "2026-07-20T00:00:00+00:00",
        "company": "Stripe",
        "ats": "greenhouse",
        "tier": 2,
    }
    defaults.update(kwargs)
    return NormalizedJob(**defaults)


RESUME = ResumeProfile(text="blinkit quick-commerce sql python", keywords=[])


def test_hard_filters_passes_ideal_job():
    passed, reason = passes_hard_filters(_job(), max_days=30, hiring_mba=True)
    assert passed is True
    assert reason == "matched"


def test_hard_filters_rejects_non_internship():
    passed, _ = passes_hard_filters(
        _job(
            title="Senior Product Manager",
            content="Full-time senior role. 10+ years experience required.",
        ),
        max_days=30,
        hiring_mba=True,
    )
    assert passed is False


def test_hard_filters_rejects_non_us():
    passed, reason = passes_hard_filters(
        _job(location="London, UK"),
        max_days=30,
        hiring_mba=True,
    )
    assert passed is False
    assert reason == "non_us_location"


def test_score_job_high_match():
    result = score_job(_job(), RESUME)
    assert result.score >= 7
    assert "product" in result.role_types


def test_score_job_includes_resume_boost():
    result = score_job(_job(), RESUME)
    assert result.breakdown.get("resume_boost", 0) >= 1
