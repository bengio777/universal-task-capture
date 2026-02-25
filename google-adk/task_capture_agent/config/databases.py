"""Notion database IDs and schemas for task routing.

Ported from the Claude Skill (SKILL.md). Maps each category to its
Notion database ID and defines the properties each database expects.
"""

MASTER_DB_ID = "c20d0a8a-48eb-4556-824a-8db6d41afabd"
NEEDS_SORTING_DB_ID = "f1a5fa34-3113-4212-b12c-1c1a5fa58955"

TOPIC_DATABASES = {
    "Shopping / Errands": {
        "data_source_id": "4601cd6c-0145-43bb-842f-5aa0ea21e3f2",
        "name": "Shopping & Errands",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Location", "Cost Estimate", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Technical / Dev": {
        "data_source_id": "91b88e19-dcde-43b2-a969-d713b3dfd28d",
        "name": "Technical Tasks",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Project", "Repo", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Class / Study": {
        "data_source_id": "3c36c983-099b-48e5-9484-5b878bdd95bb",
        "name": "Study To-Dos",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Class", "Topic", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Content / Writing": {
        "data_source_id": "8dea9c69-3698-4b10-9f04-d8fd629e1937",
        "name": "Content Pipeline",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Platform", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Business / Sales": {
        "data_source_id": "4953aef4-0aad-4021-a47a-f463f64587bb",
        "name": "Business Tasks",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Company", "Contact", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Personal": {
        "data_source_id": "37eab999-4369-4842-bdf6-6dda3be3142e",
        "name": "Personal To-Dos",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Area", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Workflow / Process": {
        "data_source_id": "dece1175-e5bc-4562-995e-afb6edc4ff9a",
        "name": "Workflow Tasks",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Workflow", "Type", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Social / Community": {
        "data_source_id": "541404e0-43a5-4722-8d4d-d298ab9d8ed9",
        "name": "Social & Community",
        "required_fields": ["Task", "Priority", "Status"],
        "optional_fields": ["Event / Group", "Location", "Notes"],
        "defaults": {"Priority": "Medium", "Status": "To Do"},
    },
    "Needs Sorting": {
        "data_source_id": NEEDS_SORTING_DB_ID,
        "name": "Needs Sorting",
        "required_fields": ["Task", "Status"],
        "optional_fields": ["Suggested Category", "Reason", "Notes"],
        "defaults": {"Status": "Unsorted"},
    },
}
