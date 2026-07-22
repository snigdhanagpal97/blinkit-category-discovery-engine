#!/usr/bin/env python3
"""Validate Greenhouse board tokens listed in config/companies.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "companies.yaml"


def validate_token(token: str, timeout: int = 15) -> tuple[bool, int, int]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "MBA-Scraper-Validator/1.0"})
    if response.status_code != 200:
        return False, response.status_code, 0
    payload = response.json()
    return True, response.status_code, len(payload.get("jobs", []))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--all", action="store_true", help="Validate disabled companies too")
    args = parser.parse_args()

    raw = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    companies = raw.get("companies", [])

    print(f"{'Company':<24} {'Token':<18} {'Enabled':<8} {'Status':<8} Jobs")
    print("-" * 72)

    valid_enabled = 0
    for entry in companies:
        if not args.all and not entry.get("enabled", False):
            continue
        token = entry["board_token"]
        ok, status, count = validate_token(token)
        mark = "OK" if ok else "FAIL"
        if ok and entry.get("enabled", False):
            valid_enabled += 1
        print(
            f"{entry['name']:<24} {token:<18} "
            f"{str(entry.get('enabled', False)):<8} {mark:<8} {count if ok else status}"
        )

    print(f"\nValid enabled boards: {valid_enabled}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
