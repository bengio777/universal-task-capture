"""Google Sheets fallback logging for when Notion API is unavailable.

Ensures no captured task is lost even if Notion is down.
"""

import os
import json
from datetime import datetime, timezone


def log_fallback(
    title: str,
    category: str = "Unknown",
    priority: str = "Medium",
    error_message: str = "",
) -> dict:
    """Log a task to the Google Sheets fallback when Notion API fails.

    This is a safety net — call it only when create_master_record or
    create_topic_entry fails due to a Notion API error.

    Args:
        title: The raw task text.
        category: The classified category (if classification succeeded).
        priority: Task priority.
        error_message: The error that triggered the fallback.

    Returns:
        A dict confirming the fallback log entry was created.
    """
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_PATH")
    sheet_id = os.environ.get("GOOGLE_SHEETS_FALLBACK_ID")

    if not creds_path or not sheet_id:
        # No Sheets configured — log locally as last resort
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "title": title,
            "category": category,
            "priority": priority,
            "error": error_message,
            "source": "Google ADK",
        }
        fallback_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "fallback_log.jsonl"
        )
        with open(fallback_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return {"logged_to": "local_file", "path": fallback_path}

    import gspread
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(sheet_id).sheet1

    row = [
        datetime.now(timezone.utc).isoformat(),
        title,
        category,
        priority,
        "Google ADK",
        "Pending",
        error_message,
    ]
    sheet.append_row(row)
    return {"logged_to": "google_sheets", "sheet_id": sheet_id}
