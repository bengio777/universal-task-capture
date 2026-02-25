# Run Guide: Universal Task Capture — Google ADK Build

## A. What Was Built

| Artifact | What it does | Location |
|----------|-------------|----------|
| `task_capture_agent/agent.py` | Root agent — receives tasks, classifies, routes, confirms | `google-adk/task_capture_agent/agent.py` |
| `task_capture_agent/tools/notion.py` | Notion API tools (create pages, update records) | `google-adk/task_capture_agent/tools/notion.py` |
| `task_capture_agent/tools/fallback.py` | Google Sheets fallback when Notion is unavailable | `google-adk/task_capture_agent/tools/fallback.py` |
| `config/categories.py` | 8 category definitions with examples + classification rules | `google-adk/config/categories.py` |
| `config/databases.py` | 9 Notion database IDs + per-database field schemas | `google-adk/config/databases.py` |
| `tests/test_tools.py` | Unit tests for all tools + config validation | `google-adk/tests/test_tools.py` |

## B. Setup Steps

### 1. Prerequisites

- Python 3.11+ installed
- A Google Cloud account (for Gemini API key)
- Your existing Notion integration token (same one the Claude Skill uses)

### 2. Create Python environment

```bash
cd google-adk
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Get a Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `GOOGLE_GENAI_API_KEY` — your Gemini API key from step 3
- `NOTION_API_KEY` — your existing Notion integration token

The Google Sheets fallback vars are optional — skip them for now.

### 5. Run the tests

```bash
cd google-adk
python -m pytest tests/ -v
```

All tests should pass (they use mocked Notion API, no real connection needed).

### 6. Start the agent

**Terminal mode:**
```bash
cd google-adk
adk run task_capture_agent
```

**Dev UI mode (browser-based):**
```bash
cd google-adk
adk web
```
Then open the URL shown in the terminal (usually `http://localhost:8000`).

## C. First Run

### Sample inputs to try

Send these one at a time to the agent:

1. **Clear category:** `Pick up dry cleaning`
   - Expected: Classified as Shopping / Errands, routed to Shopping & Errands database
   - Confirmation: `Logged to Shopping / Errands: "Pick up dry cleaning"`

2. **Technical task:** `Fix the auth bug in the login flow`
   - Expected: Classified as Technical / Dev, routed to Technical Tasks database

3. **Ambiguous input:** `Check the thing`
   - Expected: Agent asks a clarifying question OR routes to Needs Sorting

4. **With priority:** `High priority — follow up with Acme Corp on the proposal`
   - Expected: Classified as Business / Sales with priority High

### What good output looks like

For each task, the agent should:
1. Create a master record (you'll see the tool call in the output)
2. Classify the task (no tool call — this is the agent's reasoning)
3. Create a topic entry (tool call with the matched category)
4. Update the master record (tool call to link them)
5. Confirm in 1-2 sentences

### Common first-run issues

| Issue | Fix |
|-------|-----|
| `GOOGLE_GENAI_API_KEY not set` | Check your `.env` file — the key must be set |
| `notion_client.errors.APIResponseError: 401` | Your Notion token is invalid or expired — regenerate at notion.so/my-integrations |
| `notion_client.errors.APIResponseError: 404` | The database ID doesn't exist or your integration doesn't have access — share the database with your integration |
| Agent classifies incorrectly | Check the category examples in `config/categories.py` — add more boundary examples |

## D. What to Do Next

### Running it again

Just start the agent with `adk run task_capture_agent` and send tasks. Each session is independent.

### Sharing with others

The agent is a Python package — anyone with the code + API keys can run it:
1. Clone the repo
2. Set up `.env` with their own keys
3. Run `adk run task_capture_agent`

For team access without local setup: deploy to Cloud Run (see Future section below).

### When to revisit

- **Classification accuracy drops:** Add more examples to `config/categories.py`
- **New category needed:** Add to `config/categories.py` + `config/databases.py`, create the Notion database
- **Notion schema changes:** Update field mappings in `config/databases.py`

### Future: Cloud Run Deployment

When you want the agent accessible via API (for the iOS Shortcut path or other integrations):

```bash
cd google-adk
gcloud run deploy task-capture-agent \
  --source . \
  --region us-central1 \
  --set-env-vars GOOGLE_GENAI_API_KEY=xxx,NOTION_API_KEY=xxx
```

This gives you an HTTPS endpoint you can call from iOS Shortcuts, webhooks, or other services.
