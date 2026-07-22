#!/usr/bin/env python3
"""MBA Summer 2027 internship scraper using the Greenhouse Job Board API."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from src.email_notifier import EmailNotifier
from src.filters import passes_hard_filters
from src.greenhouse_client import CompanyConfig, GreenhouseClient
from src.scorer import format_match_result, score_job
from src.storage import SeenJobsStore

ROOT = Path(__file__).resolve().parent
DEFAULT_COMPANIES_CONFIG = ROOT / "config" / "companies.yaml"
DEFAULT_PROFILE_CONFIG = ROOT / "config" / "profile.yaml"
DEFAULT_SEEN_JOBS_PATH = ROOT / "data" / "seen_jobs.json"
DEFAULT_RESULTS_PATH = ROOT / "data" / "latest_results.json"


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_companies(config_path: Path) -> tuple[list[CompanyConfig], dict[str, Any]]:
    raw = load_yaml(config_path)
    settings = raw.get("settings", {})
    companies: list[CompanyConfig] = []

    for entry in raw.get("companies", []):
        if not entry.get("enabled", False):
            continue
        companies.append(
            CompanyConfig(
                name=entry["name"],
                board_token=entry["board_token"],
                tier=int(entry.get("tier", 3)),
                enabled=True,
            )
        )

    return companies, settings


def run_scraper(
    *,
    companies_config: Path,
    profile_config: Path,
    seen_jobs_path: Path,
    results_path: Path,
    dry_run: bool = False,
    skip_email: bool = False,
    max_days_override: int | None = None,
) -> dict[str, Any]:
    profile = load_yaml(profile_config)
    companies, settings = load_companies(companies_config)

    max_days = max_days_override or int(profile.get("filters", {}).get("max_days_since_posted", 7))
    min_email_score = int(profile.get("filters", {}).get("min_match_score_for_email", 7))
    profile_name = profile.get("name", "Candidate")
    alert_email = profile.get("email")

    client = GreenhouseClient(
        timeout_seconds=int(settings.get("request_timeout_seconds", 20)),
        delay_seconds=float(settings.get("delay_between_requests_seconds", 0.5)),
        user_agent=str(settings.get("user_agent", "MBA-Internship-Scraper/1.0")),
    )
    store = SeenJobsStore(seen_jobs_path)

    all_matches: list[dict[str, Any]] = []
    stats = {
        "companies_scanned": 0,
        "jobs_fetched": 0,
        "hard_filter_passed": 0,
        "matches_found": 0,
        "new_matches": 0,
        "emails_sent": 0,
    }

    for company in companies:
        stats["companies_scanned"] += 1
        jobs = client.fetch_jobs(company)
        stats["jobs_fetched"] += len(jobs)

        for job in jobs:
            passed, reason = passes_hard_filters(job, max_days_since_posted=max_days)
            if not passed:
                logging.debug(
                    "Skipped %s — %s (%s)",
                    company.name,
                    job.get("title"),
                    reason,
                )
                continue

            stats["hard_filter_passed"] += 1
            match_score = score_job(job)
            result = format_match_result(job, company.name, match_score)
            all_matches.append(result)

    all_matches.sort(key=lambda item: (-item["score"], item["company"], item["title"]))
    stats["matches_found"] = len(all_matches)

    new_matches = store.filter_new(all_matches)
    stats["new_matches"] = len(new_matches)

    email_candidates = [
        match for match in new_matches if match["score"] >= min_email_score
    ]

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

        store.register_matches(all_matches)

    if not skip_email and email_candidates and not dry_run:
        notifier = EmailNotifier.from_env(profile_name=profile_name, recipient=alert_email)
        if notifier is None:
            logging.warning(
                "Email credentials not configured; skipping %d alert(s)",
                len(email_candidates),
            )
        else:
            notifier.send_digest(email_candidates)
            stats["emails_sent"] = len(email_candidates)

    return {
        "stats": stats,
        "matches": all_matches,
        "new_matches": new_matches,
        "email_candidates": email_candidates,
    }


def print_summary(payload: dict[str, Any]) -> None:
    stats = payload["stats"]
    print("\n=== MBA Internship Scraper Summary ===")
    print(f"Companies scanned:     {stats['companies_scanned']}")
    print(f"Jobs fetched:          {stats['jobs_fetched']}")
    print(f"Passed hard filters:   {stats['hard_filter_passed']}")
    print(f"Total matches:         {stats['matches_found']}")
    print(f"New matches:           {stats['new_matches']}")
    print(f"Emails sent (7+):      {stats['emails_sent']}")

    if payload["matches"]:
        print("\nTop matches:")
        for match in payload["matches"][:10]:
            print(
                f"  [{match['score']}/10] {match['company']} — {match['title']} "
                f"({match['location']})"
            )
            print(f"    {match['url']}")
    else:
        print("\nNo matching roles found this run.")
        print("Tip: MBA internship postings peak Aug–Nov. Widen max_days or enable more companies.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--companies-config",
        type=Path,
        default=DEFAULT_COMPANIES_CONFIG,
        help="Path to companies YAML config",
    )
    parser.add_argument(
        "--profile-config",
        type=Path,
        default=DEFAULT_PROFILE_CONFIG,
        help="Path to profile YAML config",
    )
    parser.add_argument(
        "--seen-jobs-path",
        type=Path,
        default=DEFAULT_SEEN_JOBS_PATH,
        help="Path to seen jobs JSON store",
    )
    parser.add_argument(
        "--results-path",
        type=Path,
        default=DEFAULT_RESULTS_PATH,
        help="Path to write latest results JSON",
    )
    parser.add_argument(
        "--max-days",
        type=int,
        default=None,
        help="Override max days since posted (default from profile.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and print results without saving state or sending email",
    )
    parser.add_argument(
        "--skip-email",
        action="store_true",
        help="Do not send email alerts",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    try:
        payload = run_scraper(
            companies_config=args.companies_config,
            profile_config=args.profile_config,
            seen_jobs_path=args.seen_jobs_path,
            results_path=args.results_path,
            dry_run=args.dry_run,
            skip_email=args.skip_email,
            max_days_override=args.max_days,
        )
    except Exception:
        logging.exception("Scraper run failed")
        return 1

    print_summary(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
