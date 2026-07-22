#!/usr/bin/env python3
"""Multi-ATS MBA internship scraper orchestrator — Summer 2027."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from resume_matcher import (
    format_match,
    load_resume,
    passes_hard_filters,
    score_job,
)
from scrapers.ashby_scraper import AshbyScraper
from scrapers.base import CompanyEntry, HttpClient, NormalizedJob, setup_file_logging
from scrapers.custom_scraper import CustomScraper
from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.lever_scraper import LeverScraper
from scrapers.workable_scraper import WorkableScraper

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "companies_config_comprehensive.yaml"
DEFAULT_RESUME = ROOT / "my_resume.md"
DEFAULT_PREVIOUS_JOBS = ROOT / "previous_jobs.json"
DEFAULT_RESULTS = ROOT / "data" / "latest_results.json"

logger = logging.getLogger(__name__)

SCRAPER_MAP = {
    "greenhouse": GreenhouseScraper,
    "workable": WorkableScraper,
    "lever": LeverScraper,
    "ashby": AshbyScraper,
    "custom": CustomScraper,
}

# Test mode: fast subset across ATS types (verified live endpoints)
TEST_COMPANIES = [
    "Stripe",       # Greenhouse
    "Databricks",   # Greenhouse
    "Brex",         # Greenhouse
    "OpenAI",       # Ashby
    "Notion",       # Ashby
    "BCG",          # Greenhouse
]


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_config(path: Path) -> tuple[list[CompanyEntry], dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    settings = raw.get("settings", {})
    companies: list[CompanyEntry] = []

    for entry in raw.get("companies", []):
        if not entry.get("enabled", True):
            continue
        companies.append(
            CompanyEntry(
                name=entry["name"],
                ats=entry.get("ats", "custom").lower(),
                tier=int(entry.get("tier", 3)),
                enabled=True,
                hiring_mba=bool(entry.get("hiring_mba", True)),
                board_id=str(entry.get("board_id", entry.get("board_token", ""))),
                company_id=str(entry.get("company_id", entry.get("board_id", entry.get("board_token", "")))),
                careers_url=str(entry.get("careers_url", entry.get("url", ""))),
                role_keywords=list(entry.get("role_keywords", [])),
                selectors=dict(entry.get("selectors", {})),
                api_url=str(entry.get("api_url", "")),
                notes=str(entry.get("notes", "")),
            )
        )

    return companies, settings


class PreviousJobsStore:
    """Deduplication store keyed by job ID and company+title+location."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._data: dict[str, Any] = {"jobs": {}, "dedupe_keys": {}, "last_run": None}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.save()
            return
        try:
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load previous jobs (%s); starting fresh", exc)
            self._data = {"jobs": {}, "dedupe_keys": {}, "last_run": None}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True), encoding="utf-8")

    def is_seen(self, match: dict[str, Any]) -> bool:
        job_key = f"{match['company'].lower()}::{match['job_id']}"
        dedupe = match.get("dedupe_key", "")
        if job_key in self._data.get("jobs", {}):
            return True
        if dedupe and dedupe in self._data.get("dedupe_keys", {}):
            return True
        return False

    def register(self, matches: list[dict[str, Any]]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        for match in matches:
            job_key = f"{match['company'].lower()}::{match['job_id']}"
            self._data.setdefault("jobs", {})[job_key] = {
                "company": match["company"],
                "job_id": match["job_id"],
                "title": match["title"],
                "score": match["score"],
                "first_seen_at": now,
            }
            dedupe = match.get("dedupe_key")
            if dedupe:
                self._data.setdefault("dedupe_keys", {})[dedupe] = now
        self._data["last_run"] = now
        self.save()

    def filter_new(self, matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [m for m in matches if not self.is_seen(m)]


def send_email_alerts(
    matches: list[dict[str, Any]],
    *,
    profile_name: str,
    recipient: str,
    min_score: int,
) -> int:
    """Send individual emails for high-scoring matches."""
    try:
        from src.email_notifier import EmailNotifier
    except ImportError:
        logger.warning("Email notifier unavailable")
        return 0

    candidates = [m for m in matches if m["score"] >= min_score]
    if not candidates:
        return 0

    notifier = EmailNotifier.from_env(profile_name=profile_name, recipient=recipient)
    if notifier is None:
        logger.warning("Email credentials not configured; skipping %d alert(s)", len(candidates))
        return 0

    for match in candidates:
        notifier.send_match_alert(match)
    return len(candidates)


def scrape_company(
    company: CompanyEntry,
    client: HttpClient,
) -> list[NormalizedJob]:
    scraper_cls = SCRAPER_MAP.get(company.ats)
    if scraper_cls is None:
        logger.error("%s: unknown ATS type '%s'", company.name, company.ats)
        return []

    try:
        scraper = scraper_cls(client)
        return scraper.scrape(company)
    except Exception:
        logger.exception("%s: scraper failed", company.name)
        return []


def run_orchestrator(
    *,
    config_path: Path,
    resume_path: Path,
    previous_jobs_path: Path,
    results_path: Path,
    test_mode: bool = False,
    dry_run: bool = False,
    skip_email: bool = False,
    verbose: bool = False,
    max_days_override: int | None = None,
    company_filter: list[str] | None = None,
) -> dict[str, Any]:
    configure_logging(verbose)
    setup_file_logging()

    companies, settings = load_config(config_path)
    resume = load_resume(resume_path)

    if test_mode:
        test_names = {n.lower() for n in TEST_COMPANIES}
        companies = [
            CompanyEntry(
                name=c.name,
                ats=c.ats,
                tier=c.tier,
                enabled=True,
                hiring_mba=c.hiring_mba,
                board_id=c.board_id,
                company_id=c.company_id,
                careers_url=c.careers_url,
                role_keywords=c.role_keywords,
                selectors=c.selectors,
                api_url=c.api_url,
                notes=c.notes,
            )
            for c in companies
            if c.name.lower() in test_names
        ]
        logger.info("Test mode: scraping %d companies", len(companies))

    if company_filter:
        names = {n.lower() for n in company_filter}
        companies = [c for c in companies if c.name.lower() in names]

    max_days = max_days_override or int(settings.get("max_days_since_posted", 30))
    min_email_score = int(settings.get("min_match_score_for_email", 7))
    profile_name = settings.get("candidate_name", "Snigdha Nagpal")
    alert_email = settings.get("alert_email", os.getenv("ALERT_EMAIL", ""))

    client = HttpClient(
        timeout_seconds=int(settings.get("request_timeout_seconds", 20)),
        delay_seconds=float(settings.get("delay_between_requests_seconds", 0.5)),
        max_retries=int(settings.get("max_retries", 3)),
        user_agent=str(settings.get("user_agent", "MBA-Internship-Scraper/2.0")),
    )

    store = PreviousJobsStore(previous_jobs_path)
    all_matches: list[dict[str, Any]] = []
    stats = {
        "companies_scanned": 0,
        "companies_failed": 0,
        "jobs_fetched": 0,
        "hard_filter_passed": 0,
        "matches_found": 0,
        "new_matches": 0,
        "emails_sent": 0,
        "by_ats": {},
    }

    for company in companies:
        stats["companies_scanned"] += 1
        jobs = scrape_company(company, client)
        stats["by_ats"][company.ats] = stats["by_ats"].get(company.ats, 0) + len(jobs)

        if not jobs:
            stats["companies_failed"] += 1

        stats["jobs_fetched"] += len(jobs)

        for job in jobs:
            passed, reason = passes_hard_filters(
                job,
                max_days=max_days,
                hiring_mba=company.hiring_mba,
            )
            if not passed:
                logger.debug("Skip %s — %s (%s)", company.name, job.title, reason)
                continue

            stats["hard_filter_passed"] += 1
            result = score_job(job, resume)
            all_matches.append(format_match(job, result))

    all_matches.sort(key=lambda m: (-m["score"], m["company"], m["title"]))
    stats["matches_found"] = len(all_matches)

    new_matches = store.filter_new(all_matches)
    stats["new_matches"] = len(new_matches)

    if not dry_run:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(
            json.dumps(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "stats": stats,
                    "matches": all_matches,
                    "new_matches": new_matches,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        store.register(all_matches)

    if not skip_email and not dry_run:
        stats["emails_sent"] = send_email_alerts(
            new_matches,
            profile_name=profile_name,
            recipient=alert_email,
            min_score=min_email_score,
        )

    return {"stats": stats, "matches": all_matches, "new_matches": new_matches}


def print_summary(payload: dict[str, Any]) -> None:
    stats = payload["stats"]
    print("\n=== MBA Internship Scraper (Multi-ATS) ===")
    print(f"Companies scanned:     {stats['companies_scanned']}")
    print(f"Companies w/ errors:   {stats['companies_failed']}")
    print(f"Jobs fetched:          {stats['jobs_fetched']}")
    print(f"Passed hard filters:   {stats['hard_filter_passed']}")
    print(f"Total matches:         {stats['matches_found']}")
    print(f"New matches:           {stats['new_matches']}")
    print(f"Emails sent (7+):      {stats['emails_sent']}")
    if stats.get("by_ats"):
        print(f"Jobs by ATS:           {stats['by_ats']}")

    if payload["matches"]:
        print("\nTop matches:")
        for match in payload["matches"][:10]:
            print(
                f"  [{match['score']}/10] {match['company']} — {match['title']} "
                f"({match['location']}) [{match['ats']}]"
            )
            print(f"    {match['url']}")
    else:
        print("\nNo matching roles found.")
        print("Tip: MBA 2027 postings peak Aug–Nov. Try --max-days 60 or relax filters in test.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--resume", type=Path, default=DEFAULT_RESUME)
    parser.add_argument("--previous-jobs", type=Path, default=DEFAULT_PREVIOUS_JOBS)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--test", action="store_true", help="Run fast subset across ATS types")
    parser.add_argument("--dry-run", action="store_true", help="No state save or email")
    parser.add_argument("--skip-email", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--max-days", type=int, default=None)
    parser.add_argument("--company", action="append", dest="companies", help="Filter to company name(s)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = run_orchestrator(
            config_path=args.config,
            resume_path=args.resume,
            previous_jobs_path=args.previous_jobs,
            results_path=args.results,
            test_mode=args.test,
            dry_run=args.dry_run,
            skip_email=args.skip_email,
            verbose=args.verbose,
            max_days_override=args.max_days,
            company_filter=args.companies,
        )
    except Exception:
        logging.exception("Orchestrator run failed")
        return 1

    print_summary(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
