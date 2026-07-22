"""Greenhouse Job Board API client."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)

GREENHOUSE_API_BASE = "https://boards-api.greenhouse.io/v1/boards"


@dataclass(frozen=True)
class CompanyConfig:
    name: str
    board_token: str
    tier: int
    enabled: bool


class GreenhouseClient:
    def __init__(
        self,
        *,
        timeout_seconds: int = 20,
        delay_seconds: float = 0.5,
        user_agent: str = "MBA-Internship-Scraper/1.0",
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch_jobs(self, company: CompanyConfig) -> list[dict[str, Any]]:
        url = f"{GREENHOUSE_API_BASE}/{company.board_token}/jobs"
        params = {"content": "true"}

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout_seconds,
            )
            if response.status_code == 404:
                logger.warning(
                    "%s: Greenhouse board not found (token=%s)",
                    company.name,
                    company.board_token,
                )
                return []
            response.raise_for_status()
            payload = response.json()
            jobs = payload.get("jobs", [])
            logger.info("%s: fetched %d jobs", company.name, len(jobs))
            return jobs
        except requests.RequestException as exc:
            logger.error("%s: request failed — %s", company.name, exc)
            return []
        finally:
            if self.delay_seconds:
                time.sleep(self.delay_seconds)
