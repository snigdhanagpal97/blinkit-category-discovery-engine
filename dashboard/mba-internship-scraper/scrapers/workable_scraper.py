"""Workable ATS API scraper."""

from __future__ import annotations

import logging
from typing import Any

from .base import BaseScraper, CompanyEntry, NormalizedJob, parse_iso_datetime

logger = logging.getLogger(__name__)

WORKABLE_API = "https://www.workable.com/api/v1/companies/{company_id}/jobs"


class WorkableScraper(BaseScraper):
    ats_name = "workable"

    def scrape(self, company: CompanyEntry) -> list[NormalizedJob]:
        company_id = company.company_id or company.board_id
        if not company_id:
            logger.warning("%s: missing Workable company_id", company.name)
            return []

        url = WORKABLE_API.format(company_id=company_id)
        payload = self.client.get_json(url, company=company.name)
        if not payload:
            return self._greenhouse_fallback(company, company_id)

        jobs_raw = payload.get("jobs", payload if isinstance(payload, list) else [])
        if isinstance(payload, dict) and "jobs" not in payload:
            jobs_raw = []

        jobs: list[NormalizedJob] = []
        for job in jobs_raw:
            normalized = self._normalize(job, company)
            if normalized:
                jobs.append(normalized)

        logger.info("%s (Workable): fetched %d jobs", company.name, len(jobs))
        return jobs

    def _greenhouse_fallback(self, company: CompanyEntry, company_id: str) -> list[NormalizedJob]:
        from .greenhouse_scraper import GreenhouseScraper

        logger.info("%s: Workable unavailable, trying Greenhouse fallback", company.name)
        gh_company = CompanyEntry(
            name=company.name,
            ats="greenhouse",
            tier=company.tier,
            board_id=company_id,
            hiring_mba=company.hiring_mba,
            role_keywords=company.role_keywords,
        )
        return GreenhouseScraper(self.client).scrape(gh_company)

    def _normalize(self, job: dict[str, Any], company: CompanyEntry) -> NormalizedJob | None:
        job_id = job.get("shortcode") or job.get("id")
        title = job.get("title", "")
        if not job_id or not title:
            return None

        location_parts = []
        for loc in job.get("locations", []) or []:
            if isinstance(loc, dict):
                location_parts.append(loc.get("city") or loc.get("country") or "")
            else:
                location_parts.append(str(loc))
        location = ", ".join(part for part in location_parts if part) or "Unknown"

        url = job.get("url") or job.get("application_url", "")
        content = job.get("description", "") or job.get("full_description", "") or ""

        updated = job.get("published") or job.get("created_at")

        return NormalizedJob(
            id=str(job_id),
            title=title,
            location=location,
            url=url,
            content=content,
            updated_at=parse_iso_datetime(updated),
            company=company.name,
            ats=self.ats_name,
            tier=company.tier,
            raw=job,
        )
