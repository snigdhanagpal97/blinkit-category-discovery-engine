"""Persistent storage for previously seen jobs."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SeenJobsStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._data: dict[str, Any] = {"jobs": {}, "last_run": None}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.save()
            return

        try:
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not load seen jobs store (%s); starting fresh", exc)
            self._data = {"jobs": {}, "last_run": None}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    @staticmethod
    def job_key(company: str, job_id: str) -> str:
        return f"{company.lower()}::{job_id}"

    def has_seen(self, company: str, job_id: str) -> bool:
        return self.job_key(company, job_id) in self._data.get("jobs", {})

    def mark_seen(self, company: str, job_id: str, *, score: int, title: str) -> None:
        key = self.job_key(company, job_id)
        self._data.setdefault("jobs", {})[key] = {
            "company": company,
            "job_id": job_id,
            "title": title,
            "score": score,
            "first_seen_at": datetime.now(timezone.utc).isoformat(),
        }

    def mark_run_complete(self) -> None:
        self._data["last_run"] = datetime.now(timezone.utc).isoformat()

    def filter_new(self, matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
        new_matches: list[dict[str, Any]] = []
        for match in matches:
            if self.has_seen(match["company"], match["job_id"]):
                continue
            new_matches.append(match)
        return new_matches

    def register_matches(self, matches: list[dict[str, Any]]) -> None:
        for match in matches:
            self.mark_seen(
                match["company"],
                match["job_id"],
                score=match["score"],
                title=match["title"],
            )
        self.mark_run_complete()
        self.save()
