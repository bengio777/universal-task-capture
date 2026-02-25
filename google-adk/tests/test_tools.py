"""Unit tests for Notion and fallback tools.

Uses mocked Notion API responses to test tool logic without
requiring a live Notion connection.
"""

import os
import json
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Ensure config is importable
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from task_capture_agent.config.databases import MASTER_DB_ID, TOPIC_DATABASES
from task_capture_agent.tools.notion import (
    create_master_record,
    create_topic_entry,
    update_master_record,
    _build_properties,
)
from task_capture_agent.tools.fallback import log_fallback


# --- _build_properties tests ---

class TestBuildProperties:
    def test_title_field(self):
        result = _build_properties({"Task": "Buy milk"})
        assert result["Task"] == {"title": [{"text": {"content": "Buy milk"}}]}

    def test_select_field(self):
        result = _build_properties({"Status": "Pending"})
        assert result["Status"] == {"select": {"name": "Pending"}}

    def test_rich_text_field(self):
        result = _build_properties({"Notes": "Some notes"})
        assert result["Notes"] == {"rich_text": [{"text": {"content": "Some notes"}}]}

    def test_number_field(self):
        result = _build_properties({"Cost Estimate": 25.50})
        assert result["Cost Estimate"] == {"number": 25.50}

    def test_none_values_skipped(self):
        result = _build_properties({"Task": "Test", "Notes": None})
        assert "Notes" not in result
        assert "Task" in result


# --- create_master_record tests ---

class TestCreateMasterRecord:
    @patch("task_capture_agent.tools.notion._get_client")
    def test_creates_page_with_correct_db(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.pages.create.return_value = {
            "id": "page-123",
            "url": "https://notion.so/page-123",
        }
        mock_get_client.return_value = mock_client

        result = create_master_record("Pick up dry cleaning")

        call_kwargs = mock_client.pages.create.call_args[1]
        assert call_kwargs["parent"]["data_source_id"] == MASTER_DB_ID
        assert result["page_id"] == "page-123"
        assert result["url"] == "https://notion.so/page-123"

    @patch("task_capture_agent.tools.notion._get_client")
    def test_default_priority_medium(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.pages.create.return_value = {"id": "x", "url": "y"}
        mock_get_client.return_value = mock_client

        create_master_record("Test task")

        props = mock_client.pages.create.call_args[1]["properties"]
        assert props["Priority"] == {"select": {"name": "Medium"}}

    @patch("task_capture_agent.tools.notion._get_client")
    def test_custom_priority(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.pages.create.return_value = {"id": "x", "url": "y"}
        mock_get_client.return_value = mock_client

        create_master_record("Urgent task", priority="High")

        props = mock_client.pages.create.call_args[1]["properties"]
        assert props["Priority"] == {"select": {"name": "High"}}


# --- create_topic_entry tests ---

class TestCreateTopicEntry:
    @patch("task_capture_agent.tools.notion._get_client")
    def test_routes_to_correct_database(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.pages.create.return_value = {
            "id": "topic-456",
            "url": "https://notion.so/topic-456",
        }
        mock_get_client.return_value = mock_client

        result = create_topic_entry(
            category="Shopping / Errands",
            title="Buy groceries",
        )

        call_kwargs = mock_client.pages.create.call_args[1]
        expected_db = TOPIC_DATABASES["Shopping / Errands"]["data_source_id"]
        assert call_kwargs["parent"]["data_source_id"] == expected_db
        assert result["database_name"] == "Shopping & Errands"

    @patch("task_capture_agent.tools.notion._get_client")
    def test_unknown_category_routes_to_needs_sorting(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.pages.create.return_value = {"id": "ns-1", "url": "u"}
        mock_get_client.return_value = mock_client

        result = create_topic_entry(
            category="Nonexistent Category",
            title="Mystery task",
        )

        call_kwargs = mock_client.pages.create.call_args[1]
        expected_db = TOPIC_DATABASES["Needs Sorting"]["data_source_id"]
        assert call_kwargs["parent"]["data_source_id"] == expected_db
        assert result["database_name"] == "Needs Sorting"

    @patch("task_capture_agent.tools.notion._get_client")
    def test_extra_fields_mapped(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.pages.create.return_value = {"id": "t-1", "url": "u"}
        mock_get_client.return_value = mock_client

        create_topic_entry(
            category="Technical / Dev",
            title="Fix auth bug",
            project="login-service",
            repo="github.com/example/login",
        )

        props = mock_client.pages.create.call_args[1]["properties"]
        assert "Project" in props
        assert "Repo" in props


# --- update_master_record tests ---

class TestUpdateMasterRecord:
    @patch("task_capture_agent.tools.notion._get_client")
    def test_updates_status_and_category(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = update_master_record(
            page_id="page-123",
            status="Routed",
            category="Personal",
            topic_link="https://notion.so/topic-789",
        )

        mock_client.pages.update.assert_called_once()
        assert result["updated"] is True
        assert result["status"] == "Routed"


# --- log_fallback tests ---

class TestLogFallback:
    def test_logs_to_local_file_when_no_sheets(self, monkeypatch):
        monkeypatch.delenv("GOOGLE_SHEETS_CREDENTIALS_PATH", raising=False)
        monkeypatch.delenv("GOOGLE_SHEETS_FALLBACK_ID", raising=False)

        # Point fallback to a temp file
        import tempfile
        tmp_dir = tempfile.mkdtemp()
        fallback_file = os.path.join(tmp_dir, "fallback_log.jsonl")
        monkeypatch.setattr(
            "task_capture_agent.tools.fallback.os.path.join",
            lambda *args: fallback_file,
        )

        result = log_fallback(
            title="Test task",
            category="Personal",
            error_message="Notion 503",
        )

        assert result["logged_to"] == "local_file"
        with open(fallback_file) as f:
            entry = json.loads(f.readline())
        assert entry["title"] == "Test task"
        assert entry["error"] == "Notion 503"


# --- Config validation tests ---

class TestConfig:
    def test_all_categories_have_database(self):
        """Every category in CATEGORIES should map to a topic database."""
        from task_capture_agent.config.categories import CATEGORIES
        for cat in CATEGORIES:
            assert cat in TOPIC_DATABASES, f"Category '{cat}' has no database mapping"

    def test_all_databases_have_required_fields(self):
        """Every topic database must define required_fields."""
        for name, db in TOPIC_DATABASES.items():
            assert "data_source_id" in db, f"{name} missing database_id"
            assert "required_fields" in db, f"{name} missing required_fields"
            assert "Task" in db["required_fields"], f"{name} missing 'Task' field"
