"""
app.py
Flask server that exposes GET /calendar.ics as a live Notion calendar feed.

Usage:
    python app.py
    # Subscribe in Google Calendar / Apple Calendar to:
    # http://localhost:5000/calendar.ics
"""

from flask import Flask, Response, jsonify
from notion2ics import generate_ics

app = Flask(__name__)


@app.route("/calendar.ics")
def calendar_feed() -> Response:
    """Return an up-to-date ICS feed fetched live from Notion."""
    try:
        ics_bytes = generate_ics()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Notion API error: {exc}"}), 502

    return Response(
        ics_bytes,
        status=200,
        mimetype="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=calendar.ics",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@app.route("/")
def index() -> Response:
    return jsonify(
        {
            "feed": "/calendar.ics",
            "usage": "Subscribe your calendar app to http://<host>:5000/calendar.ics",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
