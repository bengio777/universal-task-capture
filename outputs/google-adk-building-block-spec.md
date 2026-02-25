# AI Building Block Spec: Universal Task Capture — Google ADK Build

## Execution Pattern

**Pattern:** Single Agent (`LlmAgent`) with custom tools
**Interaction Mode:** Interactive (local CLI), with path to autonomous via Cloud Run API

**Reasoning:**
- 5 of 6 steps are deterministic API calls — these are tool functions, not separate agents
- Only classification (Step 3) requires LLM reasoning — the agent handles this natively
- A SequentialAgent with multiple LlmAgents would add unnecessary LLM calls for what are just Notion writes
- Single expertise domain — no need for multi-agent orchestration
- Matches the simplicity of the original Claude Skill pattern

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Platform | Google ADK (Python) | User's target platform. Mature implementation, rich docs. |
| Model | Gemini 2.0 Flash | Fast, cheap, strong at classification. Native to ADK — zero config. |
| Integration approach | Custom tools (Notion Python SDK) | Simpler than MCP for a standalone app. Direct API calls via `notion-client`. |
| Deployment | Local first (`adk agent run`), Cloud Run later | Start simple, graduate to API endpoint when needed. |
| Fallback | Google Sheets (gspread) + local JSONL | Two-tier fallback: Sheets if configured, local file as last resort. |

## Scenario Summary

| Field | Value |
|-------|-------|
| **Workflow Name** | Universal Task and To-Do Capture |
| **Description** | Capture any task, classify by topic, route to correct Notion database |
| **Process Outcome** | Classified task in topic DB + linked master intake record |
| **Trigger** | User sends text to ADK agent via CLI or API |
| **Type** | Automated |
| **Business Process** | Personal Productivity |

## Step-by-Step Decomposition

| Step | Name | Autonomy Level | Building Block | ADK Implementation | HITL Gate |
|------|------|---------------|----------------|-------------------|-----------|
| 1 | Capture Input | AI-Semi-Autonomous | Agent input parsing | Agent receives text natively | None |
| 1b | Create Master Record | AI-Deterministic | Tool | `create_master_record` function | None |
| 2 | Classify | AI-Autonomous | Agent reasoning | Inline LLM classification via instructions | None |
| 3 | Route | AI-Deterministic | Tool | `create_topic_entry` function | None |
| 4 | Link | AI-Deterministic | Tool | `update_master_record` function | None |
| 5 | Confirm | AI-Deterministic | Agent output | Agent returns formatted confirmation | None |

## Autonomy Spectrum

```
|--Deterministic----|---Semi-Autonomous---|------Autonomous------|
   Steps 1b,3,4,5       Step 1 (Capture)      Step 2 (Classify)
```

- 5 of 6 steps are deterministic tool calls
- 1 step is autonomous — classification is the only LLM judgment call
- No human-in-the-loop gates — confidence threshold + Needs Sorting replaces human review

## Agent Configuration

| Component | Value |
|-----------|-------|
| **Name** | `task_capture_agent` |
| **Model** | `gemini-2.0-flash` |
| **Description** | Captures tasks, classifies by topic, routes to Notion |
| **Instruction** | Classification prompt with 8 category defs, 3-4 examples each, confidence rules, 6-step pipeline |
| **Tools** | `create_master_record`, `create_topic_entry`, `update_master_record`, `log_fallback` |
| **Output Key** | Not used — single agent, no state passing needed |

### Tool Specifications

| Tool | Purpose | Inputs | Output |
|------|---------|--------|--------|
| `create_master_record` | Audit trail entry in master DB | title, priority | page_id, url |
| `create_topic_entry` | Route task to topic database | category, title, priority, notes, **extra_fields | page_id, url, database_name |
| `update_master_record` | Link master to topic, update status | page_id, status, category, topic_link, confidence | updated, page_id, status |
| `log_fallback` | Backup when Notion fails | title, category, priority, error_message | logged_to, path/sheet_id |

## Context Inventory

| Artifact | Type | Location | Status |
|----------|------|----------|--------|
| Category definitions | Python config | `config/categories.py` | Built |
| Database mapping | Python config | `config/databases.py` | Built |
| Agent instructions | Embedded in agent.py | `task_capture_agent/agent.py` | Built |
| Classification prompt | Part of agent instructions | Inline | Built |

## Tools and Connectors

| Tool | Purpose | Integration |
|------|---------|-------------|
| Notion API | Create/update pages (10 databases) | `notion-client` Python SDK |
| Google Sheets | Fallback logging | `gspread` + service account |
| Gemini API | Classification reasoning | Native to ADK (`google-adk`) |

## Integration Research

| Integration | Availability | Notes |
|-------------|-------------|-------|
| `notion-client` (PyPI) | Available | Official Notion SDK for Python. Stable, well-maintained. |
| `google-adk` (PyPI) | Available | v1.25.0+. Requires `GOOGLE_GENAI_API_KEY` env var. |
| `gspread` (PyPI) | Available | Requires Google service account credentials. |
| Gemini 2.0 Flash | Available | Supported via ADK. Model string: `gemini-2.0-flash`. |

## Model Recommendation

**Gemini 2.0 Flash** for all steps. The workflow has one reasoning step (classification) that is well-bounded by category definitions and examples — a fast model handles this well. No steps require deep reasoning or multi-step analysis.

## Recommended Implementation Order

1. Project setup (structure, dependencies, env vars)
2. Config (category definitions, database mapping)
3. Tools (Notion API wrappers, fallback)
4. Agent definition (instructions, tool registration)
5. Tests (unit tests with mocked Notion)
6. Documentation (README, Run Guide)

## Where to Run

| Environment | How |
|-------------|-----|
| Local development | `cd google-adk && adk run task_capture_agent` |
| Local with Dev UI | `cd google-adk && adk web` |
| Cloud Run (future) | Containerize + deploy via `gcloud run deploy` |
