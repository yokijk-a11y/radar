# YOKI MONEY FINDER — Scanner V1 (add-on)

This is a safe first-stage add-on. It does not replace `index.html`.

## What it does
- Runs daily through GitHub Actions (06:17 WIB) and can also be started manually.
- Reads public RSS search results from Google News.
- Deduplicates by title + source URL.
- Stores discovery records in `data/opportunities.json`.

## Install
Copy these items into the root of `yokijk-a11y/radar`:
- `.github/workflows/daily-scan.yml`
- `scripts/scan.py`
- `requirements.txt`
- `data/opportunities.json`

Commit and push. Then open the repository's **Actions** tab and run
**YOKI Money Finder Daily Scanner** once using **Run workflow**.

## Important limitations
- RSS headlines are leads, not verified customer demand or guaranteed income.
- This V1 uses transparent keyword scoring, not an AI model.
- The existing browser `localStorage` database remains separate for now.
- Google News RSS availability/rate limits can vary.
- The workflow needs repository Actions enabled and permission to write contents.
- No API key or paid service is required for this first stage.

Next integration: update the existing dashboard to fetch `data/opportunities.json`
and show scanner discoveries separately from manually validated opportunities.
