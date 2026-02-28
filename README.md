# notioncalendar2ics

Converts a Notion database into an ICS calendar feed, compatible with **Google Calendar** and **Apple Calendar**.

## Features

- Reads all pages from a Notion database (no temporal filter — includes past events)
- Supports single dates and date ranges (start + end)
- Handles cursor-based pagination (databases with >100 items)
- Each event includes: title, date/time, Notion page URL
- Standalone script (`notion2ics.py`) that writes `calendar.ics`
- Flask server (`app.py`) with a live `GET /calendar.ics` endpoint for direct URL subscription

## Setup

### 1. Create a Notion integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a new integration and copy the **Internal Integration Secret**
3. Open your Notion database → `···` menu → **Connections** → add your integration

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

| Variable | Description | Default |
|---|---|---|
| `NOTION_API_KEY` | Integration secret (`secret_…`) | — |
| `NOTION_DATABASE_ID` | Database ID from its URL | — |
| `DATE_PROPERTY` | Name of the date property in Notion | `Date` |

## Usage

### Generate a static ICS file

```bash
python notion2ics.py
# → calendar.ics is created in the same directory
```

### Start the live feed server

```bash
python app.py
# → http://localhost:5000/calendar.ics
```

Subscribe to `http://localhost:5000/calendar.ics` in Google Calendar or Apple Calendar — each sync fetches fresh data from Notion.

## Project structure

```
notioncalendar2ics/
├── notion2ics.py     # Core logic + standalone script
├── app.py            # Flask live feed server
├── requirements.txt
├── .env.example
└── .gitignore
```
