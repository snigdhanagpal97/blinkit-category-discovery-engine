"""Custom HTML scraper for companies with proprietary career sites."""

from __future__ import annotations

import logging
import re
from html import unescape
from typing import Any
from urllib.parse import urljoin

from .base import BaseScraper, CompanyEntry, NormalizedJob

logger = logging.getLogger(__name__)

WHITESPACE_RE = re.compile(r"\s+")
HTML_TAG_RE = re.compile(r"<[^>]+>")


class CustomScraper(BaseScraper):
    ats_name = "custom"

    def scrape(self, company: CompanyEntry) -> list[NormalizedJob]:
        if not company.careers_url:
            logger.warning("%s: missing careers_url for custom scraper", company.name)
            return []

        html = self.client.get_html(company.careers_url, company=company.name)
        if not html:
            return []

        selectors = company.selectors or {}
        jobs: list[NormalizedJob] = []

        if selectors.get("job_card"):
            jobs = self._scrape_with_selectors(html, company, selectors)
        else:
            jobs = self._scrape_json_ld(html, company)

        if not jobs:
            jobs = self._scrape_link_patterns(html, company)

        logger.info("%s (Custom): fetched %d jobs", company.name, len(jobs))
        return jobs

    def _scrape_with_selectors(
        self,
        html: str,
        company: CompanyEntry,
        selectors: dict[str, str],
    ) -> list[NormalizedJob]:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("beautifulsoup4 required for custom scraping — pip install beautifulsoup4")
            return self._scrape_link_patterns(html, company)

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(selectors["job_card"])
        jobs: list[NormalizedJob] = []

        for idx, card in enumerate(cards):
            title_el = card.select_one(selectors.get("title", "a"))
            loc_el = card.select_one(selectors.get("location", ""))
            link_el = card.select_one(selectors.get("link", "a"))

            title = self._clean_text(title_el.get_text() if title_el else "")
            location = self._clean_text(loc_el.get_text() if loc_el else "Unknown")
            href = link_el.get("href", "") if link_el else ""
            url = urljoin(company.careers_url, href) if href else company.careers_url

            if not title:
                continue

            jobs.append(
                NormalizedJob(
                    id=f"custom-{company.name.lower().replace(' ', '-')}-{idx}",
                    title=title,
                    location=location,
                    url=url,
                    content=title,
                    updated_at=None,
                    company=company.name,
                    ats=self.ats_name,
                    tier=company.tier,
                    raw={"title": title, "location": location, "url": url},
                )
            )

        return jobs

    def _scrape_json_ld(self, html: str, company: CompanyEntry) -> list[NormalizedJob]:
        import json

        jobs: list[NormalizedJob] = []
        for match in re.finditer(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE,
        ):
            try:
                data = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") not in ("JobPosting", "JobPosting[]"):
                    if item.get("@type") == "ItemList":
                        for element in item.get("itemListElement", []):
                            posting = element.get("item", element)
                            job = self._job_from_json_ld(posting, company)
                            if job:
                                jobs.append(job)
                    continue

                job = self._job_from_json_ld(item, company)
                if job:
                    jobs.append(job)

        return jobs

    def _job_from_json_ld(
        self, item: dict[str, Any], company: CompanyEntry
    ) -> NormalizedJob | None:
        title = item.get("title", "")
        if not title:
            return None

        location = "Unknown"
        job_location = item.get("jobLocation", {})
        if isinstance(job_location, dict):
            address = job_location.get("address", {})
            if isinstance(address, dict):
                parts = [
                    address.get("addressLocality", ""),
                    address.get("addressRegion", ""),
                    address.get("addressCountry", ""),
                ]
                location = ", ".join(p for p in parts if p) or "Unknown"

        url = item.get("url") or item.get("hiringOrganization", {}).get("sameAs", "")
        content = item.get("description", "") or title
        job_id = item.get("identifier", {}).get("value") if isinstance(item.get("identifier"), dict) else title

        return NormalizedJob(
            id=f"jsonld-{company.name.lower()}-{str(job_id)[:40]}",
            title=title,
            location=location,
            url=url or company.careers_url,
            content=content,
            updated_at=item.get("datePosted"),
            company=company.name,
            ats=self.ats_name,
            tier=company.tier,
            raw=item,
        )

    def _scrape_link_patterns(self, html: str, company: CompanyEntry) -> list[NormalizedJob]:
        """Last-resort: extract job-like anchor tags from careers pages."""
        keywords = company.role_keywords or [
            "intern",
            "mba",
            "associate",
            "analyst",
            "product",
            "strategy",
        ]
        pattern = re.compile(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            re.DOTALL | re.IGNORECASE,
        )
        jobs: list[NormalizedJob] = []
        seen_titles: set[str] = set()

        for idx, match in enumerate(pattern.finditer(html)):
            href, raw_title = match.group(1), match.group(2)
            title = self._clean_text(raw_title)
            if len(title) < 8 or len(title) > 120:
                continue
            title_lower = title.lower()
            if not any(kw.lower() in title_lower for kw in keywords):
                continue
            if title_lower in seen_titles:
                continue
            seen_titles.add(title_lower)

            url = urljoin(company.careers_url, href)
            jobs.append(
                NormalizedJob(
                    id=f"link-{company.name.lower()}-{idx}",
                    title=title,
                    location="Unknown",
                    url=url,
                    content=title,
                    updated_at=None,
                    company=company.name,
                    ats=self.ats_name,
                    tier=company.tier,
                    raw={"title": title, "url": url},
                )
            )

        return jobs[:100]

    @staticmethod
    def _clean_text(value: str) -> str:
        text = HTML_TAG_RE.sub(" ", unescape(value))
        return WHITESPACE_RE.sub(" ", text).strip()
