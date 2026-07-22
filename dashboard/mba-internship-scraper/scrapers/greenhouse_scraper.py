"""Greenhouse Job Board API scraper."""

from __future__ import annotations

import logging
from typing import Any

from .base import BaseScraper, CompanyEntry, NormalizedJob, parse_iso_datetime

logger = logging.getLogger(__name__)

GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{board_id}/jobs"


class GreenhouseScraper(BaseScraper):
    ats_name = "greenhouse"

    def scrape(self, company: CompanyEntry) -> list[NormalizedJob]:
        board_id = company.board_id or company.company_id
        if not board_id:
            logger.warning("%s: missing Greenhouse board_id", company.name)
            return []

        url = GREENHOUSE_API.format(board_id=board_id)
        payload = self.client.get_json(url, params={"content": "true"}, company=company.name)
        if not payload:
            return self._html_fallback(company, board_id)

        jobs_raw = payload.get("jobs", [])
        jobs: list[NormalizedJob] = []
        for job in jobs_raw:
            normalized = self._normalize(job, company)
            if normalized:
                jobs.append(normalized)

        logger.info("%s (Greenhouse): fetched %d jobs", company.name, len(jobs))
        return jobs

    def _html_fallback(self, company: CompanyEntry, board_id: str) -> list[NormalizedJob]:
        """Fallback when API fails: scrape public board HTML listing."""
        from .custom_scraper import CustomScraper

        logger.info("%s: trying Greenhouse HTML fallback", company.name)
        fallback = CompanyEntry(
            name=company.name,
            ats="custom",
            tier=company.tier,
            enabled=True,
            hiring_mba=company.hiring_mba,
            careers_url=f"https://boards.greenhouse.io/{board_id}",
            selectors={
                "job_card": "div.opening",
                "title": "a",
                "location": "span.location",
                "link": "a",
            },
            role_keywords=company.role_keywords,
        )
        return CustomScraper(self.client).scrape(fallback)

    def _normalize(self, job: dict[str, Any], company: CompanyEntry) -> NormalizedJob | None:
        job_id = job.get("id")
        title = job.get("title", "")
        if not job_id or not title:
            return None

        location = job.get("location", {})
        if isinstance(location, dict):
            location_name = location.get("name", "Unknown")
        else:
            location_name = str(location)

        return NormalizedJob(
            id=str(job_id),
            title=title,
            location=location_name,
            url=job.get("absolute_url", ""),
            content=job.get("content", "") or "",
            updated_at=parse_iso_datetime(job.get("updated_at")),
            company=company.name,
            ats=self.ats_name,
            tier=company.tier,
            raw=job,
        )
