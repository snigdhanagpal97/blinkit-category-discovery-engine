# MBA Summer 2027 Internship Scraper

Greenhouse-powered job alerts for Snigdha Nagpal (UNC Kenan-Flagler MBA '28).

**Quick start:** See [SETUP_GUIDE.md](./SETUP_GUIDE.md)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --dry-run --verbose
```

Runs on GitHub Actions every 6 hours. Emails new matches scoring 7+.
