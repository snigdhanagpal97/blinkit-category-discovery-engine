#!/usr/bin/env python3
"""Build companies_config_comprehensive.yaml from config/companies.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "companies.yaml"
OUTPUT = ROOT / "companies_config_comprehensive.yaml"

# Verified ATS mappings (live API probes — overrides user defaults when APIs differ)
VERIFIED_ATS: dict[str, tuple[str, dict]] = {
    "OpenAI": ("ashby", {"board_id": "openai"}),
    "Anthropic": ("greenhouse", {"board_id": "anthropic"}),
    "Perplexity": ("ashby", {"board_id": "perplexity"}),
    "xAI": ("greenhouse", {"board_id": "xai"}),
    "Brex": ("greenhouse", {"board_id": "brex"}),
    "Ramp": ("ashby", {"board_id": "ramp"}),
    "Notion": ("ashby", {"board_id": "notion"}),
    "Linear": ("ashby", {"board_id": "linear"}),
    "Anysphere": ("ashby", {"board_id": "anysphere"}),
    "Cursor": ("ashby", {"board_id": "anysphere"}),
}

# Workable slugs (fallback to Greenhouse/Ashby/custom when API unavailable)
WORKABLE = {
    "Rippling": "rippling",
    "Klarna": "klarna",
}

# Legacy Lever slugs — scraper falls back to Ashby/Greenhouse on 404
LEVER: dict[str, str] = {}

ASHBY = {
    "Notion": "notion",
    "Linear": "linear",
    "Anysphere": "anysphere",
    "Cursor": "anysphere",
}

# Custom career sites with URLs + selectors
CUSTOM_SITES: dict[str, dict] = {
    "Google": {
        "careers_url": "https://careers.google.com/jobs/results/?q=mba%20intern",
        "role_keywords": ["intern", "mba", "product", "strategy", "associate"],
    },
    "Microsoft": {
        "careers_url": "https://careers.microsoft.com/us/en/search-results?keywords=mba%20intern",
        "role_keywords": ["intern", "mba", "product", "strategy"],
    },
    "Amazon": {
        "careers_url": "https://www.amazon.jobs/en/search?base_query=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Apple": {
        "careers_url": "https://jobs.apple.com/en-us/search?search=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Meta": {
        "careers_url": "https://www.metacareers.com/jobs?q=mba%20intern",
        "role_keywords": ["intern", "mba", "product", "strategy"],
    },
    "Adobe": {
        "careers_url": "https://careers.adobe.com/us/en/search-results?keywords=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Salesforce": {
        "careers_url": "https://careers.salesforce.com/en/jobs/?search=mba%20intern",
        "role_keywords": ["intern", "mba", "product", "strategy"],
    },
    "McKinsey": {
        "careers_url": "https://www.mckinsey.com/careers/search-jobs?query=summer%20associate",
        "role_keywords": ["summer associate", "intern", "mba"],
    },
    "Bain": {
        "careers_url": "https://www.bain.com/careers/find-a-role/?q=mba%20intern",
        "role_keywords": ["intern", "mba", "associate"],
    },
    "Kearney": {
        "careers_url": "https://kearney.com/careers/search-jobs?query=mba%20intern",
        "role_keywords": ["intern", "mba", "associate"],
    },
    "Oliver Wyman": {
        "careers_url": "https://careers.omw.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba", "associate"],
    },
    "Deloitte": {
        "careers_url": "https://apply.deloitte.com/careers/SearchJobs/?keyword=mba%20intern",
        "role_keywords": ["intern", "mba", "consulting"],
    },
    "PwC": {
        "careers_url": "https://www.pwc.com/us/en/careers/search-results.html?q=mba%20intern",
        "role_keywords": ["intern", "mba", "consulting"],
    },
    "KPMG": {
        "careers_url": "https://www.kpmguscareers.com/search/?q=mba%20intern",
        "role_keywords": ["intern", "mba", "consulting"],
    },
    "Accenture Strategy": {
        "careers_url": "https://www.accenture.com/us-en/careers/jobsearch?jk=mba%20intern",
        "role_keywords": ["intern", "mba", "strategy", "consulting"],
    },
    "EY-Parthenon": {
        "careers_url": "https://careers.ey.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba", "strategy"],
    },
    "Uber": {
        "careers_url": "https://www.uber.com/us/en/careers/list/?query=mba%20intern",
        "role_keywords": ["intern", "mba", "product", "strategy"],
    },
    "Lyft": {
        "careers_url": "https://www.lyft.com/careers?query=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "DoorDash": {
        "careers_url": "https://careers.doordash.com/jobs?query=mba%20intern",
        "role_keywords": ["intern", "mba", "product", "strategy"],
    },
    "Spotify": {
        "careers_url": "https://www.lifeatspotify.com/jobs?query=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Netflix": {
        "careers_url": "https://jobs.netflix.com/search?q=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Walmart Global Tech": {
        "careers_url": "https://careers.walmart.com/results?q=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Target": {
        "careers_url": "https://corporate.target.com/careers/search-results?query=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Nike": {
        "careers_url": "https://jobs.nike.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Lululemon": {
        "careers_url": "https://careers.lululemon.com/search/?q=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "PepsiCo": {
        "careers_url": "https://www.pepsicojobs.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Starbucks": {
        "careers_url": "https://starbucks.taleo.net/careersection/external/jobsearch.ftl?lang=en",
        "role_keywords": ["intern", "mba"],
    },
    "Verizon": {
        "careers_url": "https://mycareer.verizon.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "AT&T": {
        "careers_url": "https://www.att.jobs/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Comcast": {
        "careers_url": "https://jobs.comcast.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Delta Air Lines": {
        "careers_url": "https://delta.com/careers/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "United Airlines": {
        "careers_url": "https://careers.united.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Marriott": {
        "careers_url": "https://careers.marriott.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Hilton": {
        "careers_url": "https://jobs.hilton.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Intel": {
        "careers_url": "https://jobs.intel.com/en/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Qualcomm": {
        "careers_url": "https://careers.qualcomm.com/careers?query=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "NVIDIA": {
        "careers_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Cisco": {
        "careers_url": "https://jobs.cisco.com/jobs/SearchJobs/?keyword=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Oracle": {
        "careers_url": "https://careers.oracle.com/jobs/?keyword=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "IBM": {
        "careers_url": "https://www.ibm.com/careers/search?q=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Dell Technologies": {
        "careers_url": "https://jobs.dell.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "HP": {
        "careers_url": "https://jobs.hp.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
    "Intuit": {
        "careers_url": "https://jobs.intuit.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "ServiceNow": {
        "careers_url": "https://careers.servicenow.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Atlassian": {
        "careers_url": "https://www.atlassian.com/company/careers/all-jobs?search=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Expedia": {
        "careers_url": "https://careers.expediagroup.com/jobs/?keyword=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Booking.com": {
        "careers_url": "https://jobs.booking.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Hugging Face": {
        "careers_url": "https://huggingface.co/jobs",
        "role_keywords": ["intern", "mba", "product", "ai"],
    },
    "Weights & Biases": {
        "careers_url": "https://wandb.ai/careers",
        "role_keywords": ["intern", "product", "ai"],
    },
    "Snowflake": {
        "careers_url": "https://careers.snowflake.com/us/en/search-results?keywords=mba%20intern",
        "role_keywords": ["intern", "mba", "product"],
    },
    "Procter & Gamble": {
        "careers_url": "https://www.pgcareers.com/search-jobs?k=mba%20intern",
        "role_keywords": ["intern", "mba"],
    },
}

DEFAULT_ROLE_KEYWORDS = [
    "product",
    "strategy",
    "growth",
    "operations",
    "pm",
    "mba",
    "intern",
    "associate",
    "analyst",
]

# Additional companies from user list not in source YAML
EXTRA_COMPANIES = [
    {"name": "EY-Parthenon", "tier": 1},
    {"name": "Hugging Face", "tier": 1},
    {"name": "Weights & Biases", "tier": 1},
    {"name": "Mistral AI", "tier": 1, "board_id": "mistralai", "greenhouse": True},
    {"name": "Cohere", "tier": 1, "board_id": "cohere", "greenhouse": True},
    {"name": "Canva", "tier": 2, "board_id": "canva", "greenhouse": True},
    {"name": "Retool", "tier": 2, "board_id": "retool", "greenhouse": True},
    {"name": "Miro", "tier": 2, "board_id": "miro", "greenhouse": True},
    {"name": "DocuSign", "tier": 2, "board_id": "docusign", "greenhouse": True},
    {"name": "Alteryx", "tier": 2, "board_id": "alteryx", "greenhouse": True},
    {"name": "Splunk", "tier": 2, "board_id": "splunk", "greenhouse": True},
    {"name": "Wise", "tier": 2, "board_id": "wise", "greenhouse": True},
    {"name": "Zillow", "tier": 2, "board_id": "zillow", "greenhouse": True},
    {"name": "Etsy", "tier": 2, "board_id": "etsy", "greenhouse": True},
    {"name": "Wayfair", "tier": 2, "board_id": "wayfair", "greenhouse": True},
    {"name": "Chewy", "tier": 2, "board_id": "chewy", "greenhouse": True},
    {"name": "eBay", "tier": 2, "board_id": "ebay", "greenhouse": True},
    {"name": "Plaid", "tier": 2, "board_id": "plaid", "greenhouse": True},
    {"name": "HashiCorp", "tier": 2, "board_id": "hashicorp", "greenhouse": True},
    {"name": "Confluent", "tier": 2, "board_id": "confluent", "greenhouse": True},
    {"name": "Zendesk", "tier": 2, "board_id": "zendesk", "greenhouse": True},
    {"name": "Procter & Gamble", "tier": 3},
]


def resolve_ats(name: str, entry: dict) -> tuple[str, dict]:
    if name in VERIFIED_ATS:
        ats, extras = VERIFIED_ATS[name]
        if ats == "greenhouse":
            extras = {**extras, "api_url": f"https://boards-api.greenhouse.io/v1/boards/{extras['board_id']}/jobs"}
        return ats, extras
    if name in WORKABLE:
        return "workable", {"company_id": WORKABLE[name]}
    if name in LEVER:
        return "lever", {"company_id": LEVER[name]}
    if name in ASHBY:
        return "ashby", {"board_id": ASHBY[name]}
    if entry.get("greenhouse_verified") or entry.get("greenhouse"):
        token = entry.get("board_token") or entry.get("board_id", "")
        return "greenhouse", {
            "board_id": token,
            "api_url": f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
        }
    if name in CUSTOM_SITES:
        custom = CUSTOM_SITES[name]
        return "custom", {
            "careers_url": custom["careers_url"],
            "role_keywords": custom.get("role_keywords", DEFAULT_ROLE_KEYWORDS),
            "selectors": custom.get("selectors", {}),
        }
    # Default unverified to custom if we have notes suggesting non-greenhouse
    notes = entry.get("notes", "")
    if "not Greenhouse" in notes or "not on Greenhouse" in notes.lower():
        return "custom", {
            "careers_url": entry.get("careers_url", ""),
            "role_keywords": DEFAULT_ROLE_KEYWORDS,
        }
    # Try greenhouse with board_token anyway (may work)
    token = entry.get("board_token", "")
    if token:
        return "greenhouse", {
            "board_id": token,
            "api_url": f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs",
        }
    return "custom", {"careers_url": "", "role_keywords": DEFAULT_ROLE_KEYWORDS}


def main() -> None:
    source = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    existing_names = {c["name"] for c in source.get("companies", [])}

    companies_out: list[dict] = []

    for entry in source.get("companies", []):
        name = entry["name"]
        ats, extras = resolve_ats(name, entry)
        out = {
            "name": name,
            "ats": ats,
            "tier": entry.get("tier", 3),
            "enabled": entry.get("enabled", False),
            "hiring_mba": True,
            "role_keywords": extras.get("role_keywords", DEFAULT_ROLE_KEYWORDS),
            **{k: v for k, v in extras.items() if k != "role_keywords" or "role_keywords" in extras},
        }
        if entry.get("notes"):
            out["notes"] = entry["notes"]
        companies_out.append(out)

    for extra in EXTRA_COMPANIES:
        if extra["name"] in existing_names:
            # Update ATS for existing if needed
            for c in companies_out:
                if c["name"] == extra["name"]:
                    if extra.get("greenhouse"):
                        c["ats"] = "greenhouse"
                        c["board_id"] = extra["board_id"]
                        c["api_url"] = f"https://boards-api.greenhouse.io/v1/boards/{extra['board_id']}/jobs"
                    break
            continue
        ats, extras = resolve_ats(extra["name"], extra)
        companies_out.append(
            {
                "name": extra["name"],
                "ats": ats,
                "tier": extra.get("tier", 3),
                "enabled": extra.get("enabled", True),
                "hiring_mba": True,
                "role_keywords": extras.get("role_keywords", DEFAULT_ROLE_KEYWORDS),
                **extras,
            }
        )

    # Force verified ATS overrides
    for c in companies_out:
        name = c["name"]
        if name in VERIFIED_ATS:
            ats, extras = VERIFIED_ATS[name]
            c["ats"] = ats
            c.update(extras)
            if ats == "greenhouse":
                c["api_url"] = f"https://boards-api.greenhouse.io/v1/boards/{extras['board_id']}/jobs"
            c["enabled"] = True
        elif name in WORKABLE:
            c["ats"] = "workable"
            c["company_id"] = WORKABLE[name]
        elif name in ASHBY:
            c["ats"] = "ashby"
            c["board_id"] = ASHBY[name]
            c["enabled"] = True

    output = {
        "settings": {
            "request_timeout_seconds": source["settings"].get("request_timeout_seconds", 20),
            "delay_between_requests_seconds": source["settings"].get("delay_between_requests_seconds", 0.5),
            "max_retries": 3,
            "user_agent": source["settings"].get("user_agent", "MBA-Internship-Scraper/2.0"),
            "max_days_since_posted": 30,
            "min_match_score_for_email": 7,
            "candidate_name": "Snigdha Nagpal",
            "alert_email": "snagpal1997@gmail.com",
            "target_season": "Summer 2027",
        },
        "companies": companies_out,
    }

    OUTPUT.write_text(
        yaml.dump(output, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {len(companies_out)} companies to {OUTPUT}")


if __name__ == "__main__":
    main()
