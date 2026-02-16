# Baseline Workflow Prompt: Universal Task and To-Do Capture

## Title and Purpose

**Workflow:** Universal Task and To-Do Capture
**Description:** Capture any task, to-do, or actionable item, classify it by topic, and route it to the correct Notion database.
**Outcome:** A classified task in the correct topic database with a linked record in the master intake database.
**When to use:** Whenever the user says "log a task," "log a to-do," "capture this," "add a task," "I need to remember to...," or describes something actionable they want to track.

---

## Instructions

### Step 1: Capture Input (AI)

Receive the user's task or to-do. Be conversational and low-friction — the user wants to capture a thought before it disappears.

If the input is clear and complete, proceed immediately to classification. Do not ask unnecessary follow-up questions.

If the input is vague or could mean multiple things, ask ONE clarifying question. Example: "Is this a dev task or something personal?"

Optionally collect:
- **Urgency** — High / Medium / Low (default: Medium)
- **Context** — Any additional notes

Only ask for these if the user seems to want to add detail. Don't slow down the capture for optional fields.

### Step 1b: Create Master Record (AI)

Create a record in the **Master Task Intake** database with status "Pending":

```
Tool: notion-create-pages
parent: { "data_source_id": "<MASTER_INTAKE_DATA_SOURCE_ID>" }
pages: [{
  properties: {
    "Task": "<raw input text>",
    "Source": "Claude Skill",
    "Status": "Pending",
    "date:Created:start": "<YYYY-MM-DD>",
    "date:Created:is_datetime": 0
  }
}]
```

Save the returned page ID for Step 4.

### Step 2: Classify (AI)

Evaluate the raw input against these category definitions:

| Category | What belongs here | Examples |
|----------|------------------|----------|
| **Shopping / Errands** | Physical tasks, purchases, errands, things to pick up or drop off | "Pick up dry cleaning," "Buy birthday gift for Mom," "Return Amazon package" |
| **Technical / Dev** | Coding, debugging, infrastructure, tooling, dev environment | "Fix the auth bug in login flow," "Set up CI pipeline," "Refactor the API layer" |
| **Class / Study** | Coursework, certification prep, learning tasks, study sessions | "Review Chapter 7 on access controls," "Practice CompTIA labs," "Read the PKI section" |
| **Content / Writing** | Blog posts, articles, social media, creative writing, media production | "Draft the Substack post on AI workflows," "Write LinkedIn post," "Outline the podcast episode" |
| **Business / Sales** | Revenue, pipeline, customer-facing, operational, CRM updates | "Follow up with Acme Corp on the proposal," "Update CRM with call notes," "Prep for discovery call" |
| **Personal** | Health, relationships, life admin, non-work tasks | "Schedule dentist appointment," "Call Dad this weekend," "Renew passport" |
| **Workflow / Process** | Meta-work: building, improving, or documenting workflows and systems | "Write SOP for onboarding workflow," "Add a new category to capture skill," "Review classification accuracy" |

**Classification rules:**
- Choose the single best category. Do not multi-classify.
- If the task clearly fits one category, assign it with high confidence.
- If the task is ambiguous between two categories, ask the user ONE question to disambiguate. Example: "Should I file this under Technical/Dev or Workflow/Process?"
- If the task doesn't fit any category, classify as "Needs Sorting."

### Step 3: Route (AI)

Look up the target database from the category-to-database map:

| Category | Topic Database | Data Source ID |
|----------|---------------|----------------|
| Shopping / Errands | Shopping & Errands | `<TO_BE_CONFIGURED>` |
| Technical / Dev | Technical Tasks | `<TO_BE_CONFIGURED>` |
| Class / Study | Study To-Dos | `<TO_BE_CONFIGURED>` |
| Content / Writing | Content Pipeline | `<TO_BE_CONFIGURED>` |
| Business / Sales | Business Tasks | `<TO_BE_CONFIGURED>` |
| Personal | Personal To-Dos | `<TO_BE_CONFIGURED>` |
| Workflow / Process | Workflow Tasks | `<TO_BE_CONFIGURED>` |
| Needs Sorting | Needs Sorting | `<TO_BE_CONFIGURED>` |

Create a page in the target topic database:

```
Tool: notion-create-pages
parent: { "data_source_id": "<TOPIC_DB_DATA_SOURCE_ID>" }
pages: [{
  properties: {
    "Task": "<task description>",
    "Priority": "<urgency or Medium>",
    "Status": "To Do",
    "date:Created:start": "<YYYY-MM-DD>",
    "date:Created:is_datetime": 0
  }
}]
```

Save the returned page URL for Step 4.

### Step 4: Link (AI)

Update the master intake record from Step 1b:

```
Tool: notion-update-page
page_id: <master_record_page_id>
properties:
  "Status": "Routed"
  "Category": "<classified category>"
  "Topic Link": "<topic_page_url>"
  "Confidence": "<confidence_description>"
```

### Step 5: Confirm (AI)

Confirm briefly. Match the tone of `log-class-question` — the user is working, not doing admin.

**Success:** "Logged to [Category]: '[task summary]'"

If confidence was borderline or user was asked to clarify: "Logged to [Category] (you confirmed). '[task summary]'"

**Needs Sorting:** "Captured '[task summary]' but couldn't classify confidently — added to Needs Sorting."

**Partial failure (topic DB write failed, master succeeded):** "Captured '[task summary]' to the master log, but couldn't route to [Category] — will need manual sorting."

Keep it to one or two sentences. Include the category name so the user knows where it went.

---

## Input Requirements

| Input | Required | Format |
|-------|----------|--------|
| Task description | Yes | Natural language, any length |
| Urgency | No | High / Medium / Low (default: Medium) |
| Context | No | Free text |

The user provides these conversationally. Do not present a form — collect through natural dialogue.

---

## Context Requirements

Attach to the project or skill:
1. **Category definitions** — The classification table from Step 2 (embedded in the skill)
2. **Category-to-database map** — The routing table from Step 3 (embedded in the skill, updated as databases are created)
3. **Master intake database ID** — For Steps 1b and 4

---

## Output Format

| Output | Format | Destination |
|--------|--------|-------------|
| Topic database entry | Notion page | Correct topic database |
| Master intake record | Notion page | Master Task Intake database |
| Confirmation | 1-2 sentence text | User (conversational) |

---

## Where to Run

**Claude Code / Cowork** — Install as a skill in `.claude/skills/capture-task/SKILL.md`. Runs in any session. Invoked by trigger phrases.

**iOS Shortcut** — Separate implementation via GAS web app (not covered by this prompt — see Building Block Spec for the GAS path architecture).
