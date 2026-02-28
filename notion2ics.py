"""
notion2ics.py
Reads a Notion database and generates a calendar.ics file.
"""

import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from notion_client import Client
from icalendar import Calendar, Event, vText, vUri

load_dotenv()

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
DATE_PROPERTY = os.environ.get("DATE_PROPERTY", "Date")

OUTPUT_FILE = Path(__file__).parent / "calendar.ics"


def get_all_pages(client: Client, database_id: str) -> list[dict]:
    """Fetch every page from a Notion database, handling cursor pagination."""
    pages: list[dict] = []
    cursor = None

    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor

        response = client.request(
            path=f"databases/{database_id}/query",
            method="POST",
            body=body,
        )
        pages.extend(response.get("results", []))

        if response.get("has_more"):
            cursor = response.get("next_cursor")
        else:
            break

    return pages


def parse_date_property(date_prop: dict | None) -> tuple[date | datetime | None, date | datetime | None]:
    """
    Parse a Notion date property dict.
    Returns (start, end) where each is a date or datetime (or None).
    """
    if not date_prop or not date_prop.get("date"):
        return None, None

    date_obj = date_prop["date"]
    start_raw: str | None = date_obj.get("start")
    end_raw: str | None = date_obj.get("end")

    def parse(raw: str | None) -> date | datetime | None:
        if not raw:
            return None
        if "T" in raw:
            # datetime with optional timezone offset
            try:
                dt = datetime.fromisoformat(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                return None
        else:
            try:
                return date.fromisoformat(raw)
            except ValueError:
                return None

    return parse(start_raw), parse(end_raw)


def page_to_event(page: dict) -> Event | None:
    """Convert a Notion page dict to an icalendar Event, or None if no date."""
    properties = page.get("properties", {})

    # --- Title ---
    title_prop = properties.get("Name") or properties.get("title") or {}
    title_items = title_prop.get("title", [])
    title = "".join(t.get("plain_text", "") for t in title_items).strip() or "Untitled"

    # --- Date ---
    date_prop = properties.get(DATE_PROPERTY)
    start, end = parse_date_property(date_prop)

    if start is None:
        return None

    # --- Page URL ---
    page_url = page.get("url", "")

    event = Event()
    event.add("summary", title)
    event.add("dtstart", start)

    if end is not None:
        event.add("dtend", end)
    elif isinstance(start, date) and not isinstance(start, datetime):
        # All-day single event: DTEND = next day (RFC 5545 convention)
        from datetime import timedelta
        event.add("dtend", start + timedelta(days=1))

    if page_url:
        event.add("url", page_url)

    # Stable UID from Notion page ID
    uid = f"{page['id']}@notion"
    event.add("uid", uid)

    # Last edited time as LAST-MODIFIED
    last_edited = page.get("last_edited_time")
    if last_edited:
        try:
            dt = datetime.fromisoformat(last_edited.replace("Z", "+00:00"))
            event.add("last-modified", dt)
        except ValueError:
            pass

    return event


def build_calendar(pages: list[dict]) -> Calendar:
    """Build an icalendar Calendar from a list of Notion pages."""
    cal = Calendar()
    cal.add("prodid", "-//notion2ics//notion2ics//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", "Notion Tasks")
    cal.add("x-wr-timezone", "Europe/Rome")

    skipped = 0
    for page in pages:
        event = page_to_event(page)
        if event:
            cal.add_component(event)
        else:
            skipped += 1

    if skipped:
        print(f"  Skipped {skipped} pages without a '{DATE_PROPERTY}' date.", file=sys.stderr)

    return cal


def generate_ics() -> bytes:
    """Fetch Notion data and return the ICS file content as bytes."""
    if not NOTION_API_KEY:
        raise ValueError("NOTION_API_KEY is not set.")
    if not NOTION_DATABASE_ID:
        raise ValueError("NOTION_DATABASE_ID is not set.")

    client = Client(auth=NOTION_API_KEY, notion_version="2022-06-28")

    print(f"Fetching pages from database {NOTION_DATABASE_ID} …")
    pages = get_all_pages(client, NOTION_DATABASE_ID)
    print(f"  Found {len(pages)} pages.")

    cal = build_calendar(pages)
    return cal.to_ical()


def main() -> None:
    ics_bytes = generate_ics()
    OUTPUT_FILE.write_bytes(ics_bytes)
    print(f"Saved → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
