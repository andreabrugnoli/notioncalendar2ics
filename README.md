# notioncalendar2ics

Converts a Notion database into an ICS calendar feed, compatible with **Google Calendar** and **Apple Calendar**.

## Live feed
```
https://notioncalendar2ics.onrender.com/calendar.ics
```

## Features

- Reads all pages from a Notion database (no temporal filter — includes past events)
- Supports single dates and date ranges (start + end)
- Handles cursor-based pagination (databases with >100 items)
- Each event includes: title, date/time, Notion page URL
- Standalone script (`notion2ics.py`) that writes `calendar.ics`
- Flask server (`app.py`) with a live `GET /calendar.ics` endpoint for direct URL subscription
- Deployed on Render.com (free tier)

## Setup

### 1. Create a Notion integration

1. Go to [https://www.notion.so/profile/integrations](https://www.notion.so/profile/integrations)
2. Create a new **internal** integration and copy the **Internal Integration Secret**
3. Open your Notion database → `···` menu → **Connections** → add your integration

### 2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

| Variable | Description | Default |
|---|---|---|
| `NOTION_API_KEY` | Integration secret (`ntn_…`) | — |
| `NOTION_DATABASE_ID` | Database ID from its URL | — |
| `DATE_PROPERTY` | **Exact** name of the date property in Notion | `Date` |

> ⚠️ `DATE_PROPERTY` must match the exact property name in your database (e.g. `Data` in Italian).

## Usage

### Generate a static ICS file

```bash
python3 notion2ics.py
# → calendar.ics is created in the same directory
```

### Start the live feed server

```bash
python3 app.py
# → http://localhost:5000/calendar.ics
```

Subscribe to `http://localhost:5000/calendar.ics` in Google Calendar or Apple Calendar.

## Deployment on Render.com

1. Fork/push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com) pointing to your repo
3. Set environment variables: `NOTION_API_KEY`, `NOTION_DATABASE_ID`, `DATE_PROPERTY`
4. Start command: `python app.py`
5. Subscribe your calendar app to `https://<your-service>.onrender.com/calendar.ics`

> **Note**: Free tier spins down after 15 min inactivity (up to ~1 min cold start).
> Use [cron-job.org](https://cron-job.org) to ping the service every 10 min to keep it alive.

## Subscribe to Google Calendar

1. Google Calendar → **Altri calendari** → `+` → **Da URL**
2. Paste: `https://notioncalendar2ics.onrender.com/calendar.ics`
3. Click **Aggiungi calendario**

Google syncs approximately every 24 hours.

## Project structure

```
notioncalendar2ics/
├── notion2ics.py     # Core logic + standalone script
├── app.py            # Flask live feed server
├── render.yaml       # Render.com deployment config
├── requirements.txt
├── .env.example
└── .gitignore
```
