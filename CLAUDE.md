# notioncalendar2ics

## Project Overview
Converts a Notion database into an ICS calendar feed compatible with Google Calendar and Apple Calendar.
Includes a standalone script and a Flask web server for live URL subscription.

## Stack
- Python 3.14
- `notion-client>=2.2.1,<3.0.0` — official Notion API SDK (pinned to 2.x, v3 broke the query endpoint)
- `icalendar>=5.0.12` — RFC 5545 ICS generation
- `python-dotenv>=1.0.0` — .env config loading
- `Flask>=3.0.0` — web server for live calendar feed

## Project Structure
```
notioncalendar2ics/
├── CLAUDE.md
├── README.md
├── .env              # not committed
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml       # Render.com deployment config
├── notion2ics.py     # standalone script: reads Notion DB, writes calendar.ics
├── app.py            # Flask app: GET /calendar.ics returns live feed
└── calendar.ics      # generated output (not committed)
```

## Configuration (env vars or .env)
- `NOTION_API_KEY` — Notion integration secret (`ntn_...`)
- `NOTION_DATABASE_ID` — target database ID
- `DATE_PROPERTY` — name of the date property in Notion → **`Data`** (Italian, not `Date`)

## Key Decisions
- Reads ALL pages (no temporal filter), including past dates
- Handles cursor-based pagination (100 items per page)
- Supports single dates and date ranges (start + end)
- Page URL included as `URL` field in each VEVENT
- DTSTART/DTEND use DATE type for all-day events, DATETIME for timed events
- Flask endpoint `/calendar.ics` fetches fresh data from Notion on every request
- Uses `client.request()` directly (not `client.databases.query()`) because notion-client
  2.7.0 removed `.query()` from `DatabasesEndpoint`
- Notion API version pinned to `2022-06-28` via `Client(notion_version="2022-06-28")`
  to keep the `databases/{id}/query` endpoint working

## Running locally
```bash
# Create and activate virtual environment (required on macOS with Homebrew Python)
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Copy and fill env
cp .env.example .env

# Generate ICS file
python3 notion2ics.py

# Start live feed server
python3 app.py
# → subscribe to http://localhost:5000/calendar.ics
```

## Deployment — Render.com
- Service: https://notioncalendar2ics.onrender.com
- Plan: Free (spins down after 15 min inactivity, ~1 min cold start)
- Auto-deploys on push to `main`
- Environment variables set on Render:
  - `NOTION_API_KEY`
  - `NOTION_DATABASE_ID`
  - `DATE_PROPERTY=Data`

### Live calendar feed
```
https://notioncalendar2ics.onrender.com/calendar.ics
```
Subscribed in Google Calendar via **Altri calendari → Da URL**.
Google syncs every ~24h.

## Notion Database
- URL: https://www.notion.so/andreabrugnoli/1ee13fe71a528193a0e7d62642ce9da4
- View: https://www.notion.so/andreabrugnoli/1ee13fe71a528193a0e7d62642ce9da4?v=23013fe71a52804cbe4c000c0a5b0ec8
- Date property name: `Data` (tipo: date)
- Title property name: `Task` (tipo: title)

## Known Issues / Gotchas
- `notion-client` 3.0.0 removed `databases.query()` → pinned to `<3.0.0`
- Notion API version `2025-09-03` (default in 2.7.0) removed `databases/{id}/query` endpoint
  → forced `notion_version="2022-06-28"` in Client init
- On macOS with Homebrew Python, must use a venv (`python3 -m venv .venv`)
- `DATE_PROPERTY` must match the exact Italian name `Data`, not `Date`

## Next Steps
- [ ] Set up a cron-job.org ping every 10 min to keep Render free instance alive
- [ ] Consider upgrading to Render Starter ($7/mo) for always-on availability
- [ ] Add filtering to only export tasks with a date (currently logs skipped pages)
