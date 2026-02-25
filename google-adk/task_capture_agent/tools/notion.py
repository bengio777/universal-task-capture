"""Notion API tools for the task capture agent.

These functions are registered as ADK agent tools. Each function's
docstring and type annotations tell the LLM when and how to call them.
"""

import os
from notion_client import Client

from task_capture_agent.config.databases import MASTER_DB_ID, TOPIC_DATABASES


def _get_client() -> Client:
    """Return a Notion client using the NOTION_API_KEY env var."""
    return Client(auth=os.environ["NOTION_API_KEY"])


def _build_properties(fields: dict) -> dict:
    """Convert a flat dict into Notion property format.

    Supports title, select, number, and rich_text property types by
    inspecting the value type.
    """
    props = {}
    for key, value in fields.items():
        if value is None:
            continue
        if key == "Task":
            props[key] = {"title": [{"text": {"content": str(value)}}]}
        elif isinstance(value, (int, float)):
            props[key] = {"number": value}
        else:
            props[key] = {"select": {"name": str(value)}} if key in (
                "Status", "Priority", "Category", "Source", "Area",
                "Platform", "Type", "Class", "Confidence",
            ) else {"rich_text": [{"text": {"content": str(value)}}]}
    return props


def create_master_record(title: str, priority: str = "Medium") -> dict:
    """Create a record in the master intake database with status Pending.

    Call this FIRST, before classification. It serves as an audit trail
    so no captured task is ever lost.

    Args:
        title: The raw task text from the user.
        priority: Task priority — High, Medium, or Low. Defaults to Medium.

    Returns:
        A dict with page_id and url of the created master record.
    """
    client = _get_client()
    response = client.pages.create(
        parent={"data_source_id": MASTER_DB_ID},
        properties=_build_properties({
            "Task": title,
            "Source": "Google ADK",
            "Status": "Pending",
            "Priority": priority,
        }),
    )
    return {"page_id": response["id"], "url": response["url"]}


def create_topic_entry(
    category: str,
    title: str,
    priority: str = "Medium",
    notes: str = "",
    **extra_fields,
) -> dict:
    """Route the task to the correct topic-specific Notion database.

    Call this AFTER classification. Looks up the target database from
    the category and creates a page with domain-specific properties.

    Args:
        category: The classified category (e.g., "Shopping / Errands",
            "Technical / Dev"). Must match a key in the topic database map.
        title: The task text.
        priority: Task priority — High, Medium, or Low. Defaults to Medium.
        notes: Optional additional context or notes.
        **extra_fields: Optional domain-specific fields. For example:
            - Shopping / Errands: location, cost_estimate
            - Technical / Dev: project, repo
            - Class / Study: class_name, topic
            - Content / Writing: platform
            - Business / Sales: company, contact
            - Personal: area
            - Workflow / Process: workflow, type
            - Social / Community: event_or_group, location

    Returns:
        A dict with page_id, url, and the database_name it was routed to.
    """
    db_config = TOPIC_DATABASES.get(category)
    if not db_config:
        db_config = TOPIC_DATABASES["Needs Sorting"]
        category = "Needs Sorting"

    fields = {**db_config["defaults"], "Task": title}

    if category != "Needs Sorting":
        fields["Priority"] = priority

    if notes:
        fields["Notes"] = notes

    # Map snake_case extra_fields to Notion property names
    field_map = {
        "location": "Location",
        "cost_estimate": "Cost Estimate",
        "project": "Project",
        "repo": "Repo",
        "class_name": "Class",
        "topic": "Topic",
        "platform": "Platform",
        "company": "Company",
        "contact": "Contact",
        "area": "Area",
        "workflow": "Workflow",
        "type": "Type",
        "event_or_group": "Event / Group",
        "suggested_category": "Suggested Category",
        "reason": "Reason",
    }
    for key, value in extra_fields.items():
        notion_key = field_map.get(key)
        if notion_key and value:
            fields[notion_key] = value

    client = _get_client()
    response = client.pages.create(
        parent={"data_source_id": db_config["data_source_id"]},
        properties=_build_properties(fields),
    )
    return {
        "page_id": response["id"],
        "url": response["url"],
        "database_name": db_config["name"],
    }


def update_master_record(
    page_id: str,
    status: str,
    category: str,
    topic_link: str,
    confidence: str = "High",
) -> dict:
    """Update the master intake record after routing.

    Call this AFTER routing the task to a topic database. Links the
    master record to the topic entry and updates the status.

    Args:
        page_id: The master record page ID from create_master_record.
        status: New status — "Routed" or "Needs Sorting".
        category: The classified category name.
        topic_link: URL of the topic database entry.
        confidence: Classification confidence — "High", "Medium", or "Low".

    Returns:
        A dict confirming the update succeeded.
    """
    client = _get_client()
    client.pages.update(
        page_id=page_id,
        properties=_build_properties({
            "Status": status,
            "Category": category,
            "Topic Link": topic_link,
            "Confidence": confidence,
        }),
    )
    return {"updated": True, "page_id": page_id, "status": status}
