# MBA Internship Scraper — Setup Guide

Production-grade multi-ATS scraper for **Summer 2027 MBA internships**, tailored for Snigdha Nagpal (UNC Kenan-Flagler, Class of 2028).

## Architecture

```
job_scraper_orchestrator.py     # Main entry — routes by ATS type
├── scrapers/
│   ├── greenhouse_scraper.py   # Greenhouse Job Board API
│   ├── workable_scraper.py       # Workable API
│   ├── lever_scraper.py          # Lever API
│   ├── ashby_scraper.py          # Ashby posting API
│   └── custom_scraper.py         # HTML + CSS selectors / JSON-LD
├── resume_matcher.py             # Scoring + hard filters
├── companies_config_comprehensive.yaml
├── my_resume.md                  # Resume for match boosting
└── previous_jobs.json            # Deduplication store
```

## Quick Start

```bash
cd dashboard/mba-internship-scraper

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build/update company config from board discovery data
python scripts/build_comprehensive_config.py

# Test run (6 companies, all ATS types, no email/state)
python job_scraper_orchestrator.py --test --dry-run --verbose

# Full run
python job_scraper_orchestrator.py --verbose

# Single company
python job_scraper_orchestrator.py --company Stripe --dry-run
```

## Configuration

### `companies_config_comprehensive.yaml`

Each company entry includes:

| Field | Description |
|-------|-------------|
| `name` | Company display name |
| `ats` | `greenhouse`, `workable`, `lever`, `ashby`, or `custom` |
| `board_id` / `company_id` | ATS-specific identifier |
| `careers_url` | For custom scrapers |
| `selectors` | CSS selectors for custom HTML scraping |
| `hiring_mba` | Whether to require MBA/associate/analyst language |
| `role_keywords` | Keywords for custom link extraction |
| `tier` | 1=consulting/big tech, 2=unicorn/SaaS, 3=other (+1 score boost for tier 1-2) |
| `enabled` | Include in scrape runs |

Regenerate after updating `config/companies.yaml`:

```bash
python scripts/build_comprehensive_config.py
```

### Email Alerts (`.env`)

Copy `.env.example` to `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=your@gmail.com
```

Emails are sent **only for new jobs scoring 7+**.

Subject format: `[8/10] Stripe - Product Manager Internship (SF)`

## Filtering Logic

Hard filters (must pass all):

1. **Internship level** — intern, co-op, summer associate, MBA intern
2. **US location** — US cities/states or US remote
3. **MBA/associate/analyst** — when `hiring_mba: true`
4. **Role keywords** — product, strategy, growth, operations, PM
5. **Summer 2027** — title/description mentions 2027 (relaxed for early "MBA intern" postings)

## Scoring (1–10)

| Signal | Points |
|--------|--------|
| MBA + PM/Strategy/Growth | +4 |
| Product analytics / data | +2 |
| AI/ML / automation | +2 |
| Preferred location (SF/NYC/Seattle/Boston) | +1 |
| Company tier 1–2 | +1 |
| Resume keyword boost | up to +2 |

Resume boosts read from `my_resume.md`: quick-commerce, dynamic pricing, SQL/Python, AI product, etc.

## ATS Coverage

| ATS | Companies | API |
|-----|-----------|-----|
| Greenhouse | Stripe, Databricks, Figma, Brex, BCG, Anthropic, xAI, … | `boards-api.greenhouse.io/v1/boards/{id}/jobs` |
| Workable | Rippling, Klarna (with GH fallback) | `workable.com/api/v1/companies/{id}/jobs` |
| Lever | Legacy support (falls back to Ashby/Greenhouse) | `api.lever.co/v0/postings/{id}` |
| Ashby | OpenAI, Notion, Perplexity, Ramp, Linear, Anysphere | `api.ashbyhq.com/posting-api/job-board/{id}` |
| Custom | Google, McKinsey, Amazon, … | HTML + JSON-LD fallback |

Greenhouse API failures automatically fall back to HTML scraping of `boards.greenhouse.io/{board_id}`.

## Deduplication

`previous_jobs.json` tracks:

- `company::job_id` — primary key
- `company::title::location` — secondary dedupe key

## Error Handling

- Exponential backoff (3 retries) on all HTTP requests
- Per-company error isolation — one failure doesn't crash the run
- Logs written to `logs/scraper_YYYYMMDD_HHMMSS.log`

## GitHub Actions

Workflow: `.github/workflows/scraper.yml`

- Runs every **6 hours**
- Pre-flight `--test --dry-run` before full scrape
- Commits `previous_jobs.json` and `data/latest_results.json`

### Required Secrets

| Secret | Description |
|--------|-------------|
| `SMTP_HOST` | e.g. `smtp.gmail.com` |
| `SMTP_PORT` | e.g. `587` |
| `SMTP_USER` | Gmail address |
| `SMTP_PASSWORD` | Gmail app password |
| `ALERT_EMAIL` | Where to send alerts |

## CLI Reference

```
python job_scraper_orchestrator.py [options]

  --test              Fast subset (Stripe, Databricks, Brex, OpenAI, Notion, BCG)
  --dry-run           No state save, no email
  --skip-email        Save state but don't email
  --verbose           Debug logging
  --max-days N        Override posting recency window (default 30)
  --company NAME      Filter to specific company (repeatable)
  --config PATH       Custom YAML config
  --resume PATH       Custom resume markdown
```

## Tips for Summer 2027

- MBA internship postings typically open **Aug–Nov 2026**
- Early runs may return 0 matches — this is expected
- Widen `--max-days 60` during peak season
- Enable more companies by setting `enabled: true` in config
- Re-verify Greenhouse tokens: `python scripts/validate_boards.py --all`

## File Map

| File | Purpose |
|------|---------|
| `job_scraper_orchestrator.py` | Main orchestrator |
| `resume_matcher.py` | Filters + scoring |
| `companies_config_comprehensive.yaml` | 150+ company ATS map |
| `my_resume.md` | Your background for match reasons |
| `previous_jobs.json` | Seen jobs store |
| `data/latest_results.json` | Latest run output |
| `logs/` | Error and run logs |
| `config/companies.yaml` | Source Greenhouse board discovery |
| `config/profile.yaml` | Legacy profile (used by `main.py`) |
