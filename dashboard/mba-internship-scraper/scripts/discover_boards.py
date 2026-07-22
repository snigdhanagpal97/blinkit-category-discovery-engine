#!/usr/bin/env python3
"""Discover Greenhouse board tokens for a list of companies."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests

COMPANIES: dict[str, list[str]] = {
    "McKinsey": ["mckinsey", "mckinseyandcompany"],
    "BCG": ["bcg", "bcgbcg", "bostonconsultinggroup"],
    "Bain": ["bain", "baincompany", "bainandcompany"],
    "Bain & Company": ["bain", "baincompany"],
    "EY-Parthenon": ["eyparthenon", "parthenon", "ey", "ey-us"],
    "Strategy&": ["strategyand", "strategyandpwc", "pwcstrategy"],
    "Kearney": ["kearney", "atkearney"],
    "LEK Consulting": ["lekconsulting", "lek"],
    "Oliver Wyman": ["oliverwyman", "oliver-wyman"],
    "Accenture Strategy": ["accenture", "accenturestrategy"],
    "Deloitte": ["deloitte", "deloitteus"],
    "PwC": ["pwc", "pwccareers"],
    "KPMG": ["kpmg", "kpmgus"],
    "Databricks": ["databricks"],
    "Stripe": ["stripe"],
    "Google": ["google", "googlecareers", "googlecloud"],
    "Microsoft": ["microsoft", "microsoftcareers"],
    "Meta": ["meta", "metacareers", "facebook"],
    "Amazon": ["amazon", "amazonjobs", "aws"],
    "Apple": ["apple", "appleinc"],
    "Adobe": ["adobe", "adobecareers"],
    "Salesforce": ["salesforce", "salesforcecareers"],
    "Intuit": ["intuit", "intuitinc"],
    "ServiceNow": ["servicenow", "servicenowinc"],
    "Atlassian": ["atlassian"],
    "Cisco": ["cisco", "ciscosystems"],
    "NVIDIA": ["nvidia", "nvidiacareers"],
    "Oracle": ["oracle", "oraclecareers"],
    "SAP": ["sap", "sapcareers"],
    "IBM": ["ibm", "ibmcorp"],
    "Dell Technologies": ["dell", "delltechnologies"],
    "HP": ["hp", "hpinc"],
    "VMware by Broadcom": ["vmware", "broadcom"],
    "Snowflake": ["snowflake", "snowflakecomputing"],
    "Workday": ["workday"],
    "Qualcomm": ["qualcomm"],
    "Siemens Digital Industries": ["siemens", "siemensdigital"],
    "Samsung Research America": ["samsung", "samsungresearch"],
    "Notion": ["notion", "notionhq", "makenotion"],
    "Figma": ["figma"],
    "OpenAI": ["openai", "openaicareers"],
    "Anthropic": ["anthropic"],
    "Scale AI": ["scaleai", "scale"],
    "Rippling": ["rippling", "ripplinghq"],
    "Ramp": ["ramp", "rampinc"],
    "Brex": ["brex"],
    "Perplexity": ["perplexity", "perplexityai"],
    "xAI": ["xai", "x-ai"],
    "Cohere": ["cohere", "cohereai"],
    "Mistral AI": ["mistral", "mistralai"],
    "Glean": ["glean", "gleanwork"],
    "Writer": ["writer", "writerai"],
    "Harvey": ["harvey", "harveyai"],
    "Sierra": ["sierra", "sierraai"],
    "Runway": ["runway", "runwayml"],
    "ElevenLabs": ["elevenlabs"],
    "Character.AI": ["character", "characterai"],
    "Cursor": ["cursor", "anysphere", "cursorai"],
    "Windsurf": ["windsurf", "codeium"],
    "Together AI": ["together", "togetherai"],
    "Hugging Face": ["huggingface", "huggingface1", "hf"],
    "Weights & Biases": ["wandb", "weightsandbiases", "weightsbiases"],
    "Anysphere": ["anysphere", "cursor"],
    "Datadog": ["datadog"],
    "MongoDB": ["mongodb"],
    "Confluent": ["confluent", "confluentinc"],
    "Cloudflare": ["cloudflare"],
    "HubSpot": ["hubspot"],
    "Twilio": ["twilio"],
    "GitLab": ["gitlab"],
    "HashiCorp": ["hashicorp"],
    "Elastic": ["elastic", "elasticco"],
    "Okta": ["okta"],
    "Box": ["box", "boxinc"],
    "New Relic": ["newrelic"],
    "Splunk": ["splunk", "splunkinc"],
    "PagerDuty": ["pagerduty"],
    "Zendesk": ["zendesk"],
    "DocuSign": ["docusign"],
    "Asana": ["asana"],
    "Canva": ["canva", "canvateam"],
    "Miro": ["miro", "mirohq"],
    "Smartsheet": ["smartsheet"],
    "Alteryx": ["alteryx"],
    "Celonis": ["celonis"],
    "C3 AI": ["c3ai", "c3"],
    "Visa": ["visa"],
    "Mastercard": ["mastercard"],
    "Capital One": ["capitalone"],
    "American Express": ["americanexpress", "amex"],
    "PayPal": ["paypal"],
    "Block": ["block", "square", "blocksquare"],
    "Plaid": ["plaid"],
    "Robinhood": ["robinhood"],
    "Coinbase": ["coinbase"],
    "Chime": ["chime"],
    "SoFi": ["sofi"],
    "Affirm": ["affirm"],
    "Marqeta": ["marqeta"],
    "Adyen": ["adyen"],
    "Wise": ["wise", "transferwise"],
    "Klarna": ["klarna"],
    "Mercury": ["mercury", "mercuryhq"],
    "Uber": ["uber"],
    "Lyft": ["lyft"],
    "DoorDash": ["doordash"],
    "Instacart": ["instacart"],
    "Airbnb": ["airbnb"],
    "Expedia": ["expedia"],
    "Booking.com": ["booking", "bookingcom", "bookingholdings"],
    "Reddit": ["reddit"],
    "Pinterest": ["pinterest"],
    "Spotify": ["spotify", "spotifyjobs"],
    "Netflix": ["netflix", "netflixjobs"],
    "Disney": ["disney", "waltdisney"],
    "Roku": ["roku"],
    "Twitch": ["twitch", "twitchtv"],
    "Wayfair": ["wayfair", "wayfairinc"],
    "Etsy": ["etsy"],
    "eBay": ["ebay", "ebayinc"],
    "Chewy": ["chewy"],
    "Zillow": ["zillow"],
    "Realtor.com": ["realtor", "realtorcom", "moveinc"],
    "Walmart Global Tech": ["walmart", "walmartglobaltech"],
    "Target": ["target"],
    "Costco": ["costco"],
    "Best Buy": ["bestbuy"],
    "Nike": ["nike"],
    "Lululemon": ["lululemon"],
    "PepsiCo": ["pepsico"],
    "Starbucks": ["starbucks"],
    "AWS": ["aws", "amazonwebservices"],
    "Google Cloud": ["googlecloud"],
    "Microsoft Azure": ["microsoftazure", "azure"],
    "Akamai": ["akamai"],
    "Fastly": ["fastly"],
    "DigitalOcean": ["digitalocean"],
    "Red Hat": ["redhat"],
    "SUSE": ["suse"],
    "Pure Storage": ["purestorage"],
    "NetApp": ["netapp"],
    "Veeam": ["veeam"],
    "Nutanix": ["nutanix"],
    "AMD": ["amd"],
    "Intel": ["intel"],
    "Arm": ["arm", "armholdings"],
    "Micron": ["micron"],
    "Texas Instruments": ["texasinstruments", "ti"],
    "Synopsys": ["synopsys"],
    "Cadence": ["cadence", "cadencedesign"],
    "Marvell": ["marvell"],
    "Broadcom": ["broadcom"],
    "Seagate": ["seagate"],
    "Western Digital": ["westerndigital", "wdc"],
    "Tesla": ["tesla"],
    "Rivian": ["rivian"],
    "Lucid": ["lucid", "lucidmotors"],
    "Waymo": ["waymo"],
    "Zoox": ["zoox"],
    "Cruise": ["cruise", "getcruise"],
    "Aurora": ["aurora", "auroradriver"],
    "Motional": ["motional"],
    "Hinge Health": ["hingehealth"],
    "Omada Health": ["omadahealth", "omada"],
    "Teladoc": ["teladoc"],
    "Flatiron Health": ["flatiron", "flatironhealth"],
    "Dexcom": ["dexcom"],
    "Abbott": ["abbott"],
    "Medtronic": ["medtronic"],
    "Stryker": ["stryker"],
    "GE HealthCare": ["gehealthcare", "gehealthcarecareers"],
    "Philips": ["philips"],
    "Tempus AI": ["tempus", "tempusai"],
    "Procter & Gamble": ["pg", "proctergamble", "pgcareers"],
    "General Mills": ["generalmills"],
    "Mondelez": ["mondelez"],
    "Nestlé": ["nestle", "nestleusa"],
    "Unilever": ["unilever"],
    "Colgate-Palmolive": ["colgate", "colgatepalmolive"],
    "Kimberly-Clark": ["kimberlyclark", "kcc"],
    "Mars": ["mars", "marscareers"],
    "Danone": ["danone"],
    "Coca-Cola": ["coca-cola", "cocacola", "coke"],
    "Delta Air Lines": ["delta", "deltaairlines"],
    "United Airlines": ["united", "unitedairlines"],
    "American Airlines": ["americanairlines", "aa"],
    "Marriott": ["marriott"],
    "Hilton": ["hilton"],
    "Hyatt": ["hyatt"],
    "Booking Holdings": ["bookingholdings", "booking"],
    "Expedia Group": ["expediagroup", "expedia"],
    "Comcast": ["comcast"],
    "Verizon": ["verizon"],
    "AT&T": ["att", "attcareers"],
    "T-Mobile": ["tmobile", "t-mobile"],
    "Warner Bros. Discovery": ["wbd", "warnerbrosdiscovery"],
    "Paramount": ["paramount", "paramountglobal"],
    "NBCUniversal": ["nbcuniversal", "nbcuni"],
    "Sony Interactive Entertainment": ["sonyinteractive", "playstation", "sie"],
    "Electronic Arts": ["ea", "electronicarts"],
    "Epic Games": ["epicgames", "epic"],
    "Riot Games": ["riotgames", "riot"],
    "Workato": ["workato"],
    "LinkedIn": ["linkedin", "linkedincorp"],
    "Qualys": ["qualys"],
    "SentinelOne": ["sentinelone", "sentineloneinc"],
    "Amperity": ["amperity"],
    "Kayak": ["kayak"],
    "Starburst": ["starburst"],
    "Juniper Networks": ["juniper", "junipernetworks"],
    "Slack": ["slack", "slackhq"],
    "Dropbox": ["dropbox"],
    "Lenovo": ["lenovo"],
    "Sony PlayStation": ["playstation", "sonyinteractive"],
    "Yelp": ["yelp"],
    "Bolt": ["bolt", "bolt.eu"],
    "Verkada": ["verkada"],
    "Rubrik": ["rubrik"],
    "Roblox": ["roblox"],
    "Clari": ["clari"],
    "Align": ["align"],
    "GitHub": ["github", "githubinc"],
    "SoundCloud": ["soundcloud"],
    "Qlik": ["qlik"],
    "Onsemi": ["onsemi", "onsemiconductor"],
    "Trellix": ["trellix"],
    "Logitech": ["logitech"],
    "CrowdStrike": ["crowdstrike"],
    "Samsung": ["samsung"],
    "HPE": ["hpe", "hewlettpackardenterprise"],
    "DealCloud by Intapp": ["intapp", "dealcloud"],
    "Bolo AI": ["boloai", "bolo"],
    "Foxit": ["foxit"],
    "Bidease": ["bidease"],
    "Airtable": ["airtable"],
    "Retool": ["retool", "retoolinc", "tryretool"],
    "Linear": ["linear", "linearapp"],
    "Replit": ["replit"],
    "Zapier": ["zapier"],
    "Typeform": ["typeform"],
    "Superhuman": ["superhuman"],
    "Jasper": ["jasper", "jasperai"],
}


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def check_token(token: str) -> tuple[bool, int]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    try:
        resp = requests.get(url, timeout=12, headers={"User-Agent": "MBA-Scraper-Discovery/1.0"})
        if resp.status_code == 200:
            return True, len(resp.json().get("jobs", []))
        return False, resp.status_code
    except requests.RequestException:
        return False, 0


def main() -> None:
    results: dict[str, dict] = {}
    for company, candidates in COMPANIES.items():
        extra = slugify(company)
        tokens = list(dict.fromkeys(candidates + [extra]))
        found = None
        for token in tokens:
            ok, info = check_token(token)
            if ok:
                found = {"board_token": token, "job_count": info}
                break
            time.sleep(0.15)
        results[company] = found or {"board_token": tokens[0], "job_count": 0, "verified": False}
        if found:
            results[company]["verified"] = True
        else:
            results[company]["verified"] = False
            results[company]["status"] = info if isinstance(info, int) else 0

    out = Path(__file__).resolve().parents[1] / "data" / "board_discovery.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    verified = {k: v for k, v in results.items() if v.get("verified")}
    print(f"Verified: {len(verified)} / {len(results)}")
    for name, data in sorted(results.items()):
        mark = "OK" if data.get("verified") else "NO"
        jobs = data.get("job_count", 0) if data.get("verified") else data.get("status", "-")
        print(f"{mark:3} {name:<35} {data['board_token']:<22} {jobs}")


if __name__ == "__main__":
    main()
