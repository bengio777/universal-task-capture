# Universal Task Capture — Google ADK Build

A Google ADK agent that captures tasks, classifies them by topic using Gemini 2.0 Flash, and routes them to the correct Notion database.

This is an alternative implementation of the [Universal Task Capture](../README.md) workflow, originally built as a Claude Code skill. Same workflow, different platform.

## Architecture

```
User Input
    │
    ▼
[task_capture_agent] (Gemini 2.0 Flash)
    │
    ├─ create_master_record() → Master Intake DB (Pending)
    │
    ├─ LLM Classification → 8 categories + Needs Sorting
    │
    ├─ create_topic_entry() → Matched Topic DB
    │
    ├─ update_master_record() → Master DB (Routed + linked)
    │
    └─ Confirmation → "Logged to [Category]: [task]"
```

**Single Agent pattern** — one `LlmAgent` with 4 custom tools. Classification is the agent's native LLM reasoning; everything else is deterministic Notion API calls.

## Quick Start

```bash
# 1. Setup
cd google-adk
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your Gemini + Notion API keys

# 3. Test
python -m pytest tests/ -v

# 4. Run
adk run task_capture_agent
```

## Project Structure

```
google-adk/
├── task_capture_agent/
│   ├── agent.py              # Root agent definition
│   └── tools/
│       ├── notion.py         # Notion API tools
│       └── fallback.py       # Google Sheets fallback
├── config/
│   ├── categories.py         # 8 category definitions + rules
│   └── databases.py          # 9 Notion database IDs + schemas
├── tests/
│   └── test_tools.py         # Unit tests (mocked Notion API)
├── requirements.txt
├── .env.example
└── README.md
```

## Categories

| Category | Database |
|----------|----------|
| Shopping / Errands | Shopping & Errands |
| Technical / Dev | Technical Tasks |
| Class / Study | Study To-Dos |
| Content / Writing | Content Pipeline |
| Business / Sales | Business Tasks |
| Personal | Personal To-Dos |
| Workflow / Process | Workflow Tasks |
| Social / Community | Social & Community |
| Needs Sorting | Needs Sorting (fallback) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_GENAI_API_KEY` | Yes | Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |
| `NOTION_API_KEY` | Yes | Notion integration token |
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | No | Service account JSON for Sheets fallback |
| `GOOGLE_SHEETS_FALLBACK_ID` | No | Spreadsheet ID for fallback logging |

## Comparison with Claude Skill

| Aspect | Claude Skill | Google ADK |
|--------|-------------|------------|
| Platform | Claude Code | Google ADK (Python) |
| Model | Claude (native) | Gemini 2.0 Flash |
| Integration | Notion MCP | Notion Python SDK |
| Trigger | "log a task" in Claude | `adk run` CLI or API |
| Deployment | Claude Code session | Local / Cloud Run |
| Fallback | N/A (relies on MCP) | Google Sheets + local JSONL |
