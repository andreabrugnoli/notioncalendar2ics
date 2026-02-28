# notioncalendar2ics

## Project Overview
Converts a Notion database into an ICS calendar feed compatible with Google Calendar and Apple Calendar.
Includes a standalone script and a Flask web server for live URL subscription.

## Stack
- Python 3.10+
- `notion-client` — official Notion API SDK
- `icalendar` — RFC 5545 ICS generation
- `python-dotenv` — .env config loading
- `Flask` — optional web server for live calendar feed

## Project Structure
```
notioncalendar2ics/
├── CLAUDE.md
├── README.md
├── .env              # not committed
├── .env.example
├── .gitignore
├── requirements.txt
├── notion2ics.py     # standalone script: reads Notion DB, writes calendar.ics
├── app.py            # Flask app: GET /calendar.ics returns live feed
└── calendar.ics      # generated output (not committed)
```

## Configuration (env vars or .env)
- `NOTION_API_KEY` — Notion integration secret
- `NOTION_DATABASE_ID` — target database ID
- `DATE_PROPERTY` — name of the date property in Notion (default: `Date`)

## Key Decisions
- Reads ALL pages (no temporal filter), including past dates
- Handles cursor-based pagination (100 items per page)
- Supports single dates and date ranges (start + end)
- Page URL included as `URL` field in each VEVENT
- DTSTART/DTEND use DATE type for all-day events, DATETIME for timed events
- Flask endpoint `/calendar.ics` fetches fresh data from Notion on every request

## Running
```bash
# Install deps
pip install -r requirements.txt

# Copy and fill env
cp .env.example .env

# Generate ICS file
python notion2ics.py

# Start live feed server
python app.py
# → subscribe to http://localhost:5000/calendar.ics
```

## Notion Database
- URL: https://www.notion.so/andreabrugnoli/1ee13fe71a528193a0e7d62642ce9da4
- View: https://www.notion.so/andreabrugnoli/1ee13fe71a528193a0e7d62642ce9da4?v=23013fe71a52804cbe4c000c0a5b0ec8
