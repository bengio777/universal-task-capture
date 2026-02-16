# AI Building Block Spec: Universal Task and To-Do Capture

## Execution Pattern

**Recommended Pattern:** Skill-Powered Prompt

**Reasoning:**
- Tool use required (Notion API, Claude API, Google Sheets) → rules out plain Prompt
- One autonomous decision (classification) but the rest is deterministic → doesn't need a full Agent
- Reusable classification + routing logic → Skill pattern fits
- Single expertise domain → doesn't need Multi-Agent
- Sequential pipeline with no review gates → no orchestration complexity

**Two execution paths share the same classification logic:**

| Path | Orchestrator | Claude's Role | Infrastructure |
|------|-------------|---------------|----------------|
| Claude Skill | Claude (conversational) | Full pipeline — capture, classify, route, confirm | Notion MCP |
| iOS Shortcut | Google Apps Script | Classification only (API call) | GAS, Claude API, Notion API, Google Sheets |

---

## Scenario Summary

| Field | Value |
|-------|-------|
| **Workflow Name** | Universal Task and To-Do Capture |
| **Description** | Capture any task, to-do, or actionable item from any interface, classify it by topic, and route it to the correct Notion database |
| **Process Outcome** | A classified task logged in the correct topic database with a linked record in the master intake database |
| **Trigger** | User says "log a task," "log a to-do," or initiates capture via iOS Shortcut, Claude skill, or manual entry |
| **Type** | Automated |
| **Business Process** | Personal Productivity |

---

## Step-by-Step Decomposition

| Step | Name | Autonomy Level | Building Block(s) | Tools / Connectors | Skill Candidate | HITL Gate |
|------|------|---------------|-------------------|-------------------|----------------|-----------|
| 1 | Capture Input | AI-Semi-Autonomous (Claude) / AI-Deterministic (Shortcut) | Skill, iOS Shortcut | Notion MCP, HTTP endpoint | `capture-task` | None |
| 1b | Create Master Record | AI-Deterministic | Skill, GAS | Notion MCP / Notion API | `capture-task` | None |
| 2 | Classify | AI-Autonomous | Skill (classification prompt + logic) | Claude API (Shortcut), inline reasoning (Claude) | `capture-task` | None |
| 3 | Route | AI-Deterministic | Skill, GAS | Notion MCP / Notion API | `capture-task` | None |
| 4 | Link | AI-Deterministic | Skill, GAS | Notion MCP / Notion API | `capture-task` | None |
| 5 | Confirm | AI-Deterministic | Skill, GAS | iOS notification, conversational output | `capture-task` | None |

## Autonomy Spectrum Summary

```
|--Deterministic----|---Semi-Autonomous---|------Autonomous------|
   Steps 1b,3,4,5       Step 1 (Claude)        Step 2 (Classify)
```

- **5 of 6 steps are deterministic** — lookup, write, format. Predictable and debuggable.
- **1 step is autonomous** — classification is the only LLM judgment call.
- **No human-in-the-loop gates.** The confidence threshold + "Needs Sorting" fallback replaces human review.

---

## Skill Candidates

### `capture-task`

**Purpose:** Capture a task or to-do, classify it by topic, route it to the correct Notion database, and confirm.

**Trigger Phrases:** "log a task," "log a to-do," "capture this," "add a task," "I need to remember to..."

**Inputs:**
| Input | Required | Description |
|-------|----------|-------------|
| Raw text | Yes | The task or to-do described in natural language |
| Urgency | No | Priority level (low / medium / high) |
| Context | No | Additional notes, tags, or project reference |

**Outputs:**
| Output | Destination | Description |
|--------|-------------|-------------|
| Topic database entry | Correct Notion topic database | New page with category-appropriate properties |
| Master intake record | Master intake Notion database | Audit trail with status, category, source, link to topic entry |
| Confirmation message | User (conversational) | What was captured, where it was routed, confidence level |

**Decision Logic:**

1. **Classification** — Evaluate raw text against category definitions with boundary examples:

   | Category | Description | Example Inputs |
   |----------|-------------|----------------|
   | Shopping / Errands | Physical tasks, purchases, errands | "Pick up dry cleaning," "Buy birthday gift for Mom," "Return Amazon package" |
   | Technical / Dev | Coding, debugging, infrastructure, tooling | "Fix the auth bug in login flow," "Set up CI pipeline," "Refactor the API layer" |
   | Class / Study | Coursework, certification prep, learning tasks | "Review Chapter 7 on access controls," "Practice CompTIA labs," "Read the PKI section" |
   | Content / Writing | Blog posts, articles, social media, creative writing | "Draft the Substack post on AI workflows," "Write LinkedIn post about MEDDPICC," "Outline the podcast episode" |
   | Business / Sales | Revenue, pipeline, customer-facing, operational | "Follow up with Acme Corp on the proposal," "Update CRM with call notes," "Prep for Thursday's discovery call" |
   | Personal | Health, relationships, life admin, non-work | "Schedule dentist appointment," "Call Dad this weekend," "Renew passport" |
   | Workflow / Process | Meta-work: building, improving, documenting workflows and systems | "Write SOP for the onboarding workflow," "Add a new category to the capture skill," "Review the classification accuracy" |

2. **Confidence scoring** — Assign a confidence score (0.0–1.0):
   - >= 0.8: auto-route to matched category
   - < 0.8 (Claude skill path): ask one clarifying question, re-classify
   - < 0.8 (iOS Shortcut path): route to "Needs Sorting"

3. **Category-to-database routing** — Look up target database ID from config map. Transform raw input to match topic database schema. Create page.

4. **Master record lifecycle** — Create with status "Pending" before classification. Update to "Routed" after successful routing. Set to "Needs Sorting" if confidence is low. Set to "Failed" if Notion API errors persist.

**Failure Modes:**
| Failure | Handling |
|---------|----------|
| Notion API unavailable | Log to Google Sheets fallback, inform user, master record stays "Pending" |
| Classification confidence low | Route to Needs Sorting (Shortcut) or ask clarifying question (Claude skill) |
| Unknown category returned | Route to Needs Sorting with flag for config update |
| Topic database doesn't exist | Route to Needs Sorting with note about missing destination |
| Schema mismatch | Create with available data, flag incomplete fields |

---

## Step Sequence and Dependencies

```
Step 1: Capture Input
    │
    ├──► Step 1b: Create master record (status: Pending)
    │
    ▼
Step 2: Classify (LLM — confidence-scored)
    │
    ├── High confidence ──► Step 3: Route to topic database
    │                            │
    │                            ▼
    │                       Step 4: Link (master → Routed + relation)
    │                            │
    │                            ▼
    │                       Step 5: Confirm (success)
    │
    └── Low confidence ──► Claude path: clarify → re-classify → Step 3
                           Shortcut path: Needs Sorting → Step 4 → Step 5 (flagged)
```

**All steps are sequential.** No parallelism. Critical path = entire chain.

---

## Prerequisites

- [ ] Claude Code with Notion MCP configured
- [ ] Anthropic API key (for GAS → Claude API classification calls)
- [ ] Notion API integration token with write access to all relevant databases
- [ ] Google Apps Script environment (for iOS Shortcut path)
- [ ] iOS device with Shortcuts app (for mobile capture)
- [ ] Master intake database created in Notion
- [ ] At least one topic database created in Notion

---

## Context Inventory

| Artifact | Type | Used By | Status | Key Contents |
|----------|------|---------|--------|-------------|
| Classification Prompt | Context | Step 2 | Needs Creation | Category definitions, 3-5 examples per category, confidence scoring instructions, output format |
| Category-to-Database Map | Context / Config | Steps 2, 3 | Needs Creation | Category label → { database_id, required_fields, optional_fields, default_values } |
| Master Intake Database | Notion Database | Steps 1b, 4 | Needs Creation | Title, Category, Source, Status, Topic Link, Confidence, Timestamp |
| Topic Databases (7) | Notion Databases | Step 3 | Needs Creation | One per category with domain-specific schemas |
| Notification Templates | Context | Step 5 | Needs Creation | iOS one-line format, Claude conversational format, Needs Sorting format |
| Fallback Log | Google Sheet | Steps 1b, 3 (failure) | Needs Creation | Columns matching master database fields for reconciliation |

---

## Tools and Connectors

| Tool | Purpose | Used By Path | Integration |
|------|---------|-------------|-------------|
| **Notion MCP** | Create/update pages in master and topic databases | Claude Skill | Already configured in Claude Code |
| **Claude API** | Classification call from GAS | iOS Shortcut (via GAS) | Anthropic API key in GAS PropertiesService |
| **Notion API** | Create/update pages from GAS | iOS Shortcut (via GAS) | Notion integration token in GAS PropertiesService |
| **Google Apps Script** | HTTP endpoint + orchestration for Shortcut path | iOS Shortcut | Web app deployment |
| **Google Sheets API** | Fallback logging when Notion API fails | Both paths (failure) | Built into GAS |
| **iOS Shortcuts** | Mobile capture interface | iOS Shortcut | HTTP POST action to GAS URL |

---

## Recommended Implementation Order

### Phase 1: Core (Claude Skill Path)
1. **Create master intake database** in Notion
2. **Create 2-3 starter topic databases** (start small — Shopping/Errands, Technical/Dev, Personal)
3. **Write the `capture-task` skill** with classification prompt and category-to-database config
4. **Test end-to-end** via Claude Code: "log a task" → classify → route → link → confirm

### Phase 2: Mobile (iOS Shortcut Path)
5. **Build the GAS web app** with Claude API classification + Notion API writes
6. **Build the iOS Shortcut** with text input, HTTP POST, notification display
7. **Test end-to-end** via iPhone: tap Shortcut → type task → get confirmation

### Phase 3: Expand
8. **Add remaining topic databases** (Class/Study, Content/Writing, Business/Sales, Workflow/Process)
9. **Add the Google Sheets fallback** for resilience
10. **Tune classification** — review Needs Sorting items, update examples, adjust threshold

---

## Where to Run

| Path | Platform | Recommendation |
|------|----------|---------------|
| Claude Skill | Claude Code / Cowork | Skill installed in `.claude/skills/capture-task/SKILL.md`. Runs in any Claude Code session. |
| iOS Shortcut | Google Apps Script + iOS | GAS deployed as web app. Shortcut calls the endpoint. |
| Future: Manual Entry | Notion directly | User creates in master database, triggers automation (future — not in v1) |
