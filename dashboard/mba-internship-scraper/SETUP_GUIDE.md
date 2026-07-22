# MBA Summer 2027 Internship Scraper

Automated Greenhouse job scraper for **Snigdha Nagpal** (UNC Kenan-Flagler MBA Class of 2028), targeting Summer 2027 MBA internships in Product, Strategy, Growth, and Operations at tech and consulting companies.

## What it does

1. Polls Greenhouse Job Board APIs for configured companies every **6 hours** (GitHub Actions)
2. Filters for:
   - **USA** locations only
   - **Internship / MBA / Apprenticeship** level roles
   - **MBA hiring** language (required)
   - **Product, Strategy, Growth, or Operations** role types
   - Posted or updated in the **last 7 days**
3. Scores each match **1–10** based on product experience, analytics, AI/ML, and MBA fit
4. Emails you for **new** matches scoring **7+**
5. Tracks seen jobs to avoid duplicate alerts

## Project structure

```
mba-internship-scraper/
├── .github/workflows/scrape-jobs.yml   # Runs every 6 hours
├── config/
│   ├── companies.yaml                  # Company list + Greenhouse board tokens
│   └── profile.yaml                    # Your background + alert settings
├── data/
│   └── seen_jobs.json                  # Dedup store (committed by Actions)
├── scripts/
│   └── validate_boards.py              # Verify Greenhouse tokens
├── src/                                # Scraper modules
├── main.py                             # CLI entry point
├── requirements.txt
└── SETUP_GUIDE.md
```

---

## Step 1: Create a GitHub repository

This folder is designed to be its **own repository** (not nested inside another app's CI).

```bash
cd mba-internship-scraper
git init
git add .
git commit -m "Initial MBA internship scraper"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mba-internship-scraper.git
git push -u origin main
```

---

## Step 2: Configure companies

Edit `config/companies.yaml`:

- Set `enabled: true` for companies with a verified Greenhouse board
- Set `board_token` to the slug from `https://boards.greenhouse.io/{board_token}`

**Validate tokens:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/validate_boards.py --all
```

Currently **enabled** (verified Greenhouse boards):

| Company | Board Token |
|---------|-------------|
| BCG | `bcg` |
| Anthropic | `anthropic` |
| Databricks | `databricks` |
| Scale AI | `scaleai` |
| Figma | `figma` |
| Stripe | `stripe` |
| Airtable | `airtable` |
| Brex | `brex` |
| Chime | `chime` |
| SoFi | `sofi` |
| Roblox | `roblox` |
| Dropbox | `dropbox` |
| Reddit | `reddit` |
| Rubrik | `rubrik` |
| Kayak | `kayak` |
| Roku | `roku` |
| Amperity | `amperity` |
| Starburst | `starburst` |
| Verkada | `verkada` |
| Align | `align` |

> **Note:** McKinsey, Bain, Google, Meta, Apple, and many others use non-Greenhouse ATS platforms. Those are listed with `enabled: false` until you find their Greenhouse token (if any).

---

## Step 3: Set up Gmail app password (recommended)

1. Enable **2-Step Verification** on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Create an app password for "Mail"
4. Save the 16-character password

---

## Step 4: Add GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value | Required |
|--------|-------|----------|
| `SMTP_HOST` | `smtp.gmail.com` | Yes |
| `SMTP_PORT` | `587` | Yes |
| `SMTP_USER` | `snagpal1997@gmail.com` | Yes |
| `SMTP_PASSWORD` | Gmail app password | Yes |
| `ALERT_EMAIL` | `snagpal1997@gmail.com` | Yes |

---

## Step 5: Test locally

```bash
source .venv/bin/activate
pip install -r requirements.txt

# Dry run — no email, no state saved
python main.py --dry-run --verbose

# Full run without email
python main.py --skip-email --verbose

# Widen date window while testing (internships may be sparse off-season)
python main.py --dry-run --max-days 30 --verbose
```

---

## Step 6: Enable GitHub Actions

1. Push the repo to GitHub
2. Go to **Actions** tab → enable workflows if prompted
3. Run manually: **MBA Internship Scraper → Run workflow**
4. Scheduled runs execute every 6 hours automatically

The workflow commits updated `data/seen_jobs.json` after each run to prevent duplicate emails.

---

## Email format

**Subject:** `[8/10] Stripe - MBA Product Strategy Intern`

**Body includes:**
- Match score and breakdown
- Why the role fits your background (Blinkit/Noon analytics, D2C founder, AI PM focus)
- Key requirements snippet
- Direct link to apply

Only **new** jobs scoring **7+** trigger email.

---

## Match scoring (1–10)

| Factor | Max Points | What it checks |
|--------|------------|----------------|
| Product experience | 3 | PM language, roadmap, 0→1, cross-functional |
| Analytics / data | 3 | SQL, Python, experimentation, metrics |
| AI / ML | 2 | AI product, LLM, ML strategy |
| MBA hiring | 2 | Explicit MBA intern / business school language |
| Role fit | 2 | Product, Strategy, Growth, or Operations match |

---

## Customization

### Profile (`config/profile.yaml`)
- Update background, target roles, email, min score threshold

### Filters
Hard filters are in `src/filters.py`. Key regexes:
- `MBA_KEYWORDS` — must match for a job to qualify
- `ROLE_TYPE_KEYWORDS` — product / strategy / growth / operations
- `US_LOCATION_KEYWORDS` — USA-only gate

### Off-season testing
MBA internship postings peak **August–November** for the following summer. During off-season, use:

```bash
python main.py --dry-run --max-days 30
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No matches found | Normal off-season; widen `--max-days`; enable more companies |
| 404 for a company | Wrong board token — run `validate_boards.py` |
| Email not sending | Check GitHub Secrets; test with `python main.py --skip-email` first |
| Duplicate emails | Ensure `data/seen_jobs.json` is committed by Actions |
| Workflow push fails | Repo Settings → Actions → General → allow workflows to write |

---

## Security notes

- Never commit `.env` or SMTP passwords
- Use Gmail **App Passwords**, not your main password
- Greenhouse read API requires no API key

---

## License

Personal use — built for Snigdha Nagpal's MBA internship search.
