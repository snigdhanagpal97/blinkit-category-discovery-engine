#!/usr/bin/env python3
"""Generate config/companies.yaml from data/board_discovery.json."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT / "data" / "board_discovery.json"
OUTPUT = ROOT / "config" / "companies.yaml"

# Display order + tier assignment
SECTIONS: list[tuple[str, int, list[str]]] = [
    ("Consulting & Professional Services", 1, [
        "McKinsey", "BCG", "Bain", "EY-Parthenon", "Strategy&", "Kearney",
        "LEK Consulting", "Oliver Wyman", "Accenture Strategy", "Deloitte",
        "PwC", "KPMG",
    ]),
    ("Big Tech", 1, [
        "Google", "Microsoft", "Meta", "Amazon", "Apple", "Adobe", "Salesforce",
        "LinkedIn", "Netflix", "Spotify", "Uber", "Airbnb",
    ]),
    ("AI / ML", 1, [
        "OpenAI", "Anthropic", "Perplexity", "xAI", "Scale AI", "Cohere",
        "Mistral AI", "Glean", "Writer", "Harvey", "Sierra", "Runway",
        "ElevenLabs", "Character.AI", "Cursor", "Anysphere", "Windsurf",
        "Together AI", "Hugging Face", "Weights & Biases", "Tempus AI",
        "Bolo AI",
    ]),
    ("Enterprise SaaS & DevTools", 2, [
        "Databricks", "Snowflake", "Datadog", "MongoDB", "Confluent",
        "Cloudflare", "HubSpot", "Twilio", "GitLab", "GitHub", "HashiCorp",
        "Elastic", "Okta", "Box", "New Relic", "Splunk", "PagerDuty",
        "Zendesk", "DocuSign", "Asana", "Notion", "Canva", "Figma", "Miro",
        "Smartsheet", "Alteryx", "Celonis", "C3 AI", "Atlassian", "ServiceNow",
        "Intuit", "Workday", "Workato", "Retool", "Linear", "Replit",
        "Zapier", "Typeform", "Superhuman", "Jasper", "Airtable", "Dropbox",
        "Slack", "Clari", "Qlik", "DealCloud by Intapp", "Foxit",
    ]),
    ("Fintech & Payments", 2, [
        "Stripe", "Visa", "Mastercard", "Capital One", "American Express",
        "PayPal", "Block", "Plaid", "Brex", "Ramp", "Rippling", "Robinhood",
        "Coinbase", "Chime", "SoFi", "Affirm", "Marqeta", "Adyen", "Wise",
        "Klarna", "Mercury",
    ]),
    ("Consumer, Marketplace & Travel", 2, [
        "Lyft", "DoorDash", "Instacart", "Expedia", "Booking.com",
        "Booking Holdings", "Expedia Group", "Reddit", "Pinterest", "Disney",
        "Roku", "Twitch", "Wayfair", "Etsy", "eBay", "Chewy", "Zillow",
        "Realtor.com", "Kayak", "Yelp", "Bolt", "Roblox", "SoundCloud",
        "Bidease",
    ]),
    ("Retail & CPG", 3, [
        "Walmart Global Tech", "Target", "Costco", "Best Buy", "Nike",
        "Lululemon", "PepsiCo", "Starbucks", "Procter & Gamble",
        "General Mills", "Mondelez", "Nestlé", "Unilever",
        "Colgate-Palmolive", "Kimberly-Clark", "Mars", "Danone", "Coca-Cola",
    ]),
    ("Cloud & Infrastructure", 2, [
        "AWS", "Google Cloud", "Microsoft Azure", "Akamai", "Fastly",
        "DigitalOcean", "Red Hat", "SUSE", "Pure Storage", "NetApp", "Veeam",
        "Nutanix", "Rubrik", "Verkada", "Starburst", "Amperity",
    ]),
    ("Semiconductor & Hardware", 3, [
        "NVIDIA", "Qualcomm", "AMD", "Intel", "Arm", "Micron",
        "Texas Instruments", "Synopsys", "Cadence", "Marvell", "Broadcom",
        "Seagate", "Western Digital", "Onsemi", "Cisco", "Juniper Networks",
        "NetApp", "Lenovo", "Dell Technologies", "HP", "HPE",
        "VMware by Broadcom", "Samsung", "Samsung Research America",
        "Logitech", "Sony Interactive Entertainment", "Sony PlayStation",
    ]),
    ("Automotive & Mobility", 2, [
        "Tesla", "Rivian", "Lucid", "Waymo", "Zoox", "Cruise", "Aurora",
        "Motional",
    ]),
    ("Healthcare & Life Sciences", 2, [
        "Hinge Health", "Omada Health", "Teladoc", "Flatiron Health", "Dexcom",
        "Abbott", "Medtronic", "Stryker", "GE HealthCare", "Philips", "Align",
    ]),
    ("Travel, Hospitality & Airlines", 3, [
        "Delta Air Lines", "United Airlines", "American Airlines", "Marriott",
        "Hilton", "Hyatt",
    ]),
    ("Media, Telecom & Entertainment", 3, [
        "Comcast", "Verizon", "AT&T", "T-Mobile", "Warner Bros. Discovery",
        "Paramount", "NBCUniversal", "Electronic Arts", "Epic Games",
        "Riot Games",
    ]),
    ("Enterprise & Security (Legacy List)", 3, [
        "Oracle", "SAP", "IBM", "Qualys", "SentinelOne", "CrowdStrike",
        "Trellix", "Splunk",
    ]),
]

NOTES_OVERRIDES = {
    "Google": "Uses careers.google.com — not Greenhouse",
    "Microsoft": "Uses careers.microsoft.com — not Greenhouse",
    "Meta": "Uses metacareers.com — not Greenhouse",
    "Amazon": "Uses amazon.jobs — not Greenhouse",
    "Apple": "Uses jobs.apple.com — not Greenhouse",
    "McKinsey": "Uses mckinsey.com/careers — not Greenhouse",
    "Bain": "Uses bain.com/careers — not Greenhouse",
    "OpenAI": "Uses openai.com/careers — not Greenhouse",
    "Notion": "Uses ashby/notion careers — not Greenhouse",
    "GitHub": "Uses github.com/careers — not Greenhouse",
    "Box": "Token is boxinc (not box)",
    "Glean": "Token is gleanwork (not glean)",
    "Lucid": "Token is lucidmotors (not lucid)",
    "Flatiron Health": "Token is flatironhealth",
    "Samsung Research America": "Token is samsungresearchamerica",
    "Together AI": "Token is togetherai",
    "LinkedIn": "Greenhouse board exists but may be subset of roles",
    "HubSpot": "Greenhouse board verified (token: hubspot)",
    "Harvey": "Greenhouse board verified but currently 0 published jobs",
    "Unilever": "Greenhouse board verified (token: unilever)",
    "Accenture Strategy": "Uses accenture.com careers — not Greenhouse (404)",
}


def api_url(token: str) -> str:
    return f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


def build_entry(name: str, tier: int, discovery: dict) -> dict:
    info = discovery.get(name, {})
    token = info.get("board_token", name.lower().replace(" ", "").replace("&", ""))
    verified = bool(info.get("verified"))
    jobs = info.get("job_count", 0) if verified else 0

    notes = NOTES_OVERRIDES.get(name, "")
    if not verified and not notes:
        status = info.get("status", 404)
        notes = f"Not on Greenhouse (API probe returned {status})"

    entry = {
        "name": name,
        "tier": tier,
        "board_token": token,
        "enabled": verified,
        "greenhouse_verified": verified,
        "api_url": api_url(token),
    }
    if verified:
        entry["job_count"] = jobs
    if notes:
        entry["notes"] = notes
    return entry


def main() -> None:
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    companies: list[dict] = []
    seen: set[str] = set()

    for _section, tier, names in SECTIONS:
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            companies.append(build_entry(name, tier, discovery))

    document = {
        "settings": {
            "request_timeout_seconds": 20,
            "delay_between_requests_seconds": 0.5,
            "user_agent": "MBA-Internship-Scraper/1.0 (personal job alert; contact: snagpal1997@gmail.com)",
            "api_base": "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs",
        },
        "companies": companies,
    }

    header = """# Greenhouse board tokens — Summer 2027 MBA internship search
#
# API endpoint format:
#   https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
#
# Fields:
#   board_token          — slug from boards.greenhouse.io/{board_token}
#   enabled              — true only when greenhouse_verified is true
#   greenhouse_verified  — confirmed via live API probe
#   job_count            — published jobs at last verification
#
# Re-verify tokens: python scripts/validate_boards.py --all
# Discover new tokens: python scripts/discover_boards.py

"""
    yaml_body = yaml.dump(document, sort_keys=False, allow_unicode=True, default_flow_style=False)
    OUTPUT.write_text(header + yaml_body, encoding="utf-8")
    verified = sum(1 for c in companies if c.get("greenhouse_verified"))
    print(f"Wrote {len(companies)} companies ({verified} verified Greenhouse boards) to {OUTPUT}")


if __name__ == "__main__":
    main()
