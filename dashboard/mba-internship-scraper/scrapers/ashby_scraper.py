"""Ashby ATS public posting API scraper."""

from __future__ import annotations

import logging
from typing import Any

from .base import BaseScraper, CompanyEntry, NormalizedJob, parse_iso_datetime

logger = logging.getLogger(__name__)

ASHBY_API = "https://api.ashbyhq.com/posting-api/job-board/{board_id}"


class AshbyScraper(BaseScraper):
    ats_name = "ashby"

    def scrape(self, company: CompanyEntry) -> list[NormalizedJob]:
        board_id = company.board_id or company.company_id
        if not board_id:
            logger.warning("%s: missing Ashby board_id", company.name)
            return []

        url = ASHBY_API.format(board_id=board_id)
        payload = self.client.get_json(url, company=company.name)
        if not payload:
            return []

        jobs_raw = payload.get("jobs", [])
        jobs: list[NormalizedJob] = []
        for job in jobs_raw:
            normalized = self._normalize(job, company)
            if normalized:
                jobs.append(normalized)

        logger.info("%s (Ashby): fetched %d jobs", company.name, len(jobs))
        return jobs

    def _normalize(self, job: dict[str, Any], company: CompanyEntry) -> NormalizedJob | None:
        job_id = job.get("id")
        title = job.get("title", "")
        if not job_id or not title:
            return None

        location = job.get("location", "Unknown")
        if isinstance(location, dict):
            location = location.get("name", "Unknown")

        content_parts = [
            job.get("descriptionPlain", "") or "",
            job.get("descriptionHtml", "") or "",
        ]

        return NormalizedJob(
            id=str(job_id),
            title=title,
            location=str(location),
            url=job.get("jobUrl") or job.get("applyUrl", ""),
            content=" ".join(part for part in content_parts if part),
            updated_at=parse_iso_datetime(job.get("publishedAt") or job.get("updatedAt")),
            company=company.name,
            ats=self.ats_name,
            tier=company.tier,
            raw=job,
        )
