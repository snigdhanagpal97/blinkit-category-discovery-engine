"""Shared scraper utilities: HTTP client, retries, normalized job model."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import requests

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"


@dataclass(frozen=True)
class CompanyEntry:
    name: str
    ats: str
    tier: int = 3
    enabled: bool = True
    hiring_mba: bool = True
    board_id: str = ""
    company_id: str = ""
    careers_url: str = ""
    role_keywords: list[str] = field(default_factory=list)
    selectors: dict[str, str] = field(default_factory=dict)
    api_url: str = ""
    notes: str = ""


@dataclass
class NormalizedJob:
    id: str
    title: str
    location: str
    url: str
    content: str
    updated_at: str | None
    company: str
    ats: str
    tier: int
    raw: dict[str, Any] = field(default_factory=dict)

    def dedupe_key(self) -> str:
        loc = self.location.strip().lower()
        title = self.title.strip().lower()
        return f"{self.company.lower()}::{title}::{loc}"


def setup_file_logging(run_id: str | None = None) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = LOGS_DIR / f"scraper_{stamp}.log"
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s")
    )
    logging.getLogger().addHandler(handler)
    logger.info("Logging to %s", log_path)


class HttpClient:
    """HTTP session with exponential backoff retries."""

    def __init__(
        self,
        *,
        timeout_seconds: int = 20,
        delay_seconds: float = 0.5,
        max_retries: int = 3,
        user_agent: str = "MBA-Internship-Scraper/2.0",
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        company: str = "",
    ) -> Any | None:
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout_seconds,
                )
                if response.status_code == 404:
                    logger.warning("%s: resource not found — %s", company or "?", url)
                    return None
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                wait = min(2**attempt, 30)
                logger.error(
                    "%s: request failed (attempt %d/%d) — %s",
                    company or "?",
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt == self.max_retries:
                    return None
                time.sleep(wait)
            finally:
                if self.delay_seconds:
                    time.sleep(self.delay_seconds)
        return None

    def get_html(self, url: str, *, company: str = "") -> str | None:
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout_seconds)
                if response.status_code == 404:
                    logger.warning("%s: page not found — %s", company or "?", url)
                    return None
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                wait = min(2**attempt, 30)
                logger.error(
                    "%s: HTML fetch failed (attempt %d/%d) — %s",
                    company or "?",
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt == self.max_retries:
                    return None
                time.sleep(wait)
            finally:
                if self.delay_seconds:
                    time.sleep(self.delay_seconds)
        return None


class BaseScraper:
    ats_name: str = "base"

    def __init__(self, client: HttpClient) -> None:
        self.client = client

    def scrape(self, company: CompanyEntry) -> list[NormalizedJob]:
        raise NotImplementedError


def parse_iso_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        return dt.astimezone(timezone.utc).isoformat()
    except ValueError:
        return value
