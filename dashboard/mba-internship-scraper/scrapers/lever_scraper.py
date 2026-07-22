"""Lever ATS API scraper."""

from __future__ import annotations

import logging
from typing import Any

from .base import BaseScraper, CompanyEntry, NormalizedJob, parse_iso_datetime

logger = logging.getLogger(__name__)

LEVER_API = "https://api.lever.co/v0/postings/{company_id}"


class LeverScraper(BaseScraper):
    ats_name = "lever"

    def scrape(self, company: CompanyEntry) -> list[NormalizedJob]:
        company_id = company.company_id or company.board_id
        if not company_id:
            logger.warning("%s: missing Lever company_id", company.name)
            return []

        url = LEVER_API.format(company_id=company_id)
        payload = self.client.get_json(url, company=company.name)
        if not payload or not isinstance(payload, list):
            return self._ashby_fallback(company, company_id)

        jobs: list[NormalizedJob] = []
        for job in payload:
            normalized = self._normalize(job, company)
            if normalized:
                jobs.append(normalized)

        logger.info("%s (Lever): fetched %d jobs", company.name, len(jobs))
        return jobs

    def _ashby_fallback(self, company: CompanyEntry, company_id: str) -> list[NormalizedJob]:
        from .ashby_scraper import AshbyScraper
        from .greenhouse_scraper import GreenhouseScraper

        logger.info("%s: Lever unavailable, trying Ashby then Greenhouse", company.name)
        for scraper_cls, field, value in [
            (AshbyScraper, "board_id", company_id),
            (GreenhouseScraper, "board_id", company_id),
        ]:
            fallback = CompanyEntry(
                name=company.name,
                ats=scraper_cls.ats_name,
                tier=company.tier,
                hiring_mba=company.hiring_mba,
                role_keywords=company.role_keywords,
                **{field: value},
            )
            jobs = scraper_cls(self.client).scrape(fallback)
            if jobs:
                return jobs
        return []

    def _normalize(self, job: dict[str, Any], company: CompanyEntry) -> NormalizedJob | None:
        job_id = job.get("id")
        title = job.get("text", "") or job.get("title", "")
        if not job_id or not title:
            return None

        categories = job.get("categories", {}) or {}
        location = categories.get("location") or categories.get("allLocations", ["Unknown"])
        if isinstance(location, list):
            location_name = ", ".join(location) if location else "Unknown"
        else:
            location_name = str(location)

        content_parts = [
            job.get("descriptionPlain", "") or "",
            job.get("description", "") or "",
            " ".join(categories.get("team", []) or []),
            " ".join(categories.get("commitment", []) or []),
        ]

        return NormalizedJob(
            id=str(job_id),
            title=title,
            location=location_name,
            url=job.get("hostedUrl") or job.get("applyUrl", ""),
            content=" ".join(part for part in content_parts if part),
            updated_at=parse_iso_datetime(job.get("createdAt")),
            company=company.name,
            ats=self.ats_name,
            tier=company.tier,
            raw=job,
        )
