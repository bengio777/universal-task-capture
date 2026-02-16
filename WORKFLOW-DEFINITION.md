# Workflow Definition: Universal Task and To-Do Capture

## Scenario Metadata

| Field | Value |
|-------|-------|
| **Workflow Name** | Universal Task and To-Do Capture |
| **Description** | Capture any task, to-do, or actionable item from any interface, classify it by topic, and route it to the correct Notion database |
| **Process Outcome** | A classified task logged in the correct topic database with a linked record in the master intake database |
| **Trigger** | User says "log a task," "log a to-do," or initiates capture via iOS Shortcut, Claude skill, or manual entry |
| **Type** | Automated |
| **Business Process** | Personal Productivity |
| **Business Objective** | Eliminate friction in capturing actionable items so nothing falls through the cracks, regardless of where or how the thought occurs |
| **Current Owner(s)** | Benjamin Giordano |

---

## Refined Steps

### Step 1: Capture Input (Automation)

**Action:** Receive raw text input and optional metadata from the user through any supported interface.

**Sub-steps:**
1. Receive raw text describing the task or to-do
2. Collect optional metadata: urgency, additional context, tags
3. Identify the source channel (iOS Shortcut, Claude skill, or manual entry)
4. Package into a structured capture object: `{ raw_text, source, metadata, timestamp }`

**Decision Points:**
- Which interface initiated the capture? This determines how metadata is collected:
  - **iOS Shortcut path:** Structured form fields (text input + optional urgency picker)
  - **Claude skill path:** Conversational — Claude can ask follow-up questions if input is sparse
  - **Manual entry path:** Direct database entry (future)

**Data In:** Raw text from user, source identifier, optional metadata fields
**Data Out:** Structured capture object passed to classification

**Context Needs:**
- List of valid categories (displayed as hints or used for validation)
- Notion database IDs for routing

**Failure Modes:**
- Input is blank or too vague to classify → proceed to classification, will route to "Needs Sorting"
- iOS Shortcut fails to connect to GAS endpoint → show error notification, user retries
- Claude skill not invoked correctly → Claude asks for clarification

---

### Step 1b: Create Master Record (Automation)

**Action:** Immediately create a record in the master intake database with status "Pending" as a safety net before classification begins.

**Sub-steps:**
1. Create a page in the master intake database with: title (raw input), source, timestamp, status = "Pending"
2. Return the master record page ID for later update

**Decision Points:** None — this always fires.

**Data In:** Structured capture object from Step 1
**Data Out:** Master database page ID

**Context Needs:**
- Master intake database ID and schema

**Failure Modes:**
- Notion API fails → log to fallback (Google Sheets), continue to classification anyway (the task still gets routed, just without the audit trail entry)

---

### Step 2: Classify (AI)

**Action:** Determine the topic category for the captured input using LLM-based classification.

**Sub-steps:**
1. Send raw text + category definitions (with examples) to Claude API
2. Receive classified category + confidence score + brief reasoning
3. Evaluate confidence against threshold:
   - **Above threshold:** proceed with classified category
   - **Below threshold (iOS Shortcut path):** flag as "Needs Sorting"
   - **Below threshold (Claude skill path):** ask user a clarifying question, then re-classify

**Decision Points:**
- Confidence threshold: what score means "auto-route" vs. "needs help"?
  - Recommended starting point: 0.8 (adjust based on observed accuracy)
- Ambiguous input spanning two categories:
  - If one category scores significantly higher → use it
  - If scores are close → route to "Needs Sorting" (iOS) or ask the user (Claude skill)

**Data In:** Raw text, category definitions with 3-5 examples per category, any user-provided metadata
**Data Out:** Category label, confidence score, reasoning string (for audit trail)

**Context Needs:**
- **Classification prompt** with precise category definitions and boundary examples
- Each category needs 3-5 representative example inputs so the LLM has clear decision boundaries
- Category list must be kept in sync across all entry paths (single source of truth in config)

**Failure Modes:**
- Claude API is down → GAS returns graceful error; iOS Shortcut shows "Captured but not classified — will retry"; master record stays "Pending"
- Classification is wrong → mitigated by confidence thresholding and strong example sets; user can reclassify from master database
- Category doesn't exist in the system → route to "Needs Sorting" with a note; this itself becomes a task to resolve

---

### Step 3: Route (Automation)

**Action:** Create an entry in the correct topic-specific Notion database based on the classification result.

**Sub-steps:**
1. Look up the target topic database ID from the category-to-database mapping
2. Transform the raw input into the schema the topic database expects (each database has different properties)
3. Create the page in the topic database via Notion API
4. Return the created page ID for linking in Step 4

**Decision Points:**
- Does the topic database require fields beyond what was captured?
  - **iOS Shortcut path:** Missing fields get sensible defaults or stay blank
  - **Claude skill path:** Claude can ask for additional fields conversationally before creating
- "Needs Sorting" category: create in a dedicated Needs Sorting database or a "Needs Sorting" view in the master database

**Data In:** Classified category, raw text, metadata, category-to-database map
**Data Out:** Created Notion page ID in the topic database

**Context Needs:**
- **Category-to-database map:** config mapping each category label to its Notion topic database ID
- **Schema map:** for each category, what are the required vs. optional properties in its topic database
- Notion API credentials (integration token with write access to all topic databases)

**Failure Modes:**
- Notion API fails → retry once, then save to fallback log (Google Sheets) so nothing is lost; master record stays "Pending"
- Category maps to a database that doesn't exist yet → route to "Needs Sorting" with a note about the missing destination
- Schema mismatch (raw input doesn't map to required fields) → create with what you have, flag incomplete fields in the entry

---

### Step 4: Link (Automation)

**Action:** Update the master intake record to reflect successful routing and link it to the topic database entry.

**Sub-steps:**
1. Update the master record status from "Pending" to "Routed"
2. Add a relation (or URL reference) linking the master record to the topic database page created in Step 3
3. Set the category field on the master record

**Decision Points:**
- Relation type: Notion relation property (requires a relation column per topic database) vs. URL text field (simpler, works with any database). Start with URL field, migrate to relations when the system stabilizes.

**Data In:** Master record page ID (from Step 1b), topic page ID (from Step 3), category label
**Data Out:** Updated master record with status "Routed" and link to topic entry

**Context Needs:**
- Master intake database ID and schema
- Understanding of which field stores the topic entry link

**Failure Modes:**
- Master database write fails after topic entry succeeded → the task exists in the right place but the audit trail has a gap; not catastrophic but should be logged
- Relation property doesn't exist (new category added, master schema not updated) → fall back to URL field, flag for schema update

---

### Step 5: Confirm (Automation)

**Action:** Notify the user that capture is complete, including what was captured, where it was routed, and the classification confidence.

**Sub-steps:**
1. Build a confirmation message with: raw input summary, category, topic database name, confidence level
2. Deliver through the appropriate channel based on source:
   - **iOS Shortcut:** iOS push notification (one line)
   - **Claude skill:** conversational confirmation inline
   - **Manual entry:** UI feedback (future)

**Decision Points:**
- Confirmation format varies by source:
  - **iOS Shortcut:** Keep to one line. Example: `Logged to Shopping/Errands: "Pick up dry cleaning"`
  - **Claude skill:** Natural language. Example: "Got it — logged to your Technical/Dev database with project tag 'prd-builder'"
  - **"Needs Sorting" items:** Confirmation must say so explicitly: `Captured but couldn't classify confidently — added to Needs Sorting`

**Data In:** Category, raw text, topic page URL, confidence score, source identifier
**Data Out:** Formatted confirmation message delivered to user

**Context Needs:**
- **Notification templates** per source channel
- For iOS Shortcut: GAS response body format that the Shortcut parses into a notification
- For Claude skill: just natural language (no template needed)

**Failure Modes:**
- GAS returns an error before confirmation → Shortcut shows generic "something went wrong" notification (but entry may have been created — user can check master database)
- Notification too terse → user doesn't know where the task went; include category name at minimum
- Notification too verbose for phone → keep iOS path to one line; save details for the master record

---

## Step Sequence and Dependencies

### Flow Diagram

```
Step 1: Capture Input
    │
    ├──► Step 1b: Create master record (status: Pending)
    │
    ▼
Step 2: Classify (LLM-based, confidence-scored)
    │
    ├── High confidence ──► Step 3: Route to topic database
    │                            │
    │                            ▼
    │                       Step 4: Link (update master → Routed)
    │                            │
    │                            ▼
    │                       Step 5: Confirm (success)
    │
    └── Low confidence ──► Claude skill path: ask clarifying question → re-classify → Step 3
                           iOS Shortcut path: route to Needs Sorting → Step 4 → Step 5 (flagged)
```

### Sequential Steps
All steps are sequential. Each depends on the output of the previous step.

### Parallel Steps
None. The workflow is a single linear chain per capture event.

### Critical Path
The entire chain is the critical path: Capture → Classify → Route → Link → Confirm.

### Dependency Map
| Step | Depends On | Produces |
|------|-----------|----------|
| 1: Capture | User input | Structured capture object |
| 1b: Create Master | Step 1 output | Master record page ID |
| 2: Classify | Step 1 output | Category + confidence |
| 3: Route | Step 2 output + category-to-DB map | Topic page ID |
| 4: Link | Step 1b output + Step 3 output | Updated master record |
| 5: Confirm | Steps 2, 3, 4 outputs + source | User notification |

---

## Context Shopping List

| Artifact | Description | Used By Steps | Status | Key Contents |
|----------|-------------|---------------|--------|-------------|
| **Classification Prompt** | Prompt with category definitions and 3-5 examples per category for LLM-based classification | Step 2 | Needs Creation | Category names, descriptions, boundary examples, confidence scoring instructions, output format spec |
| **Category-to-Database Map** | Config mapping each category label to its Notion topic database ID and required/optional field schema | Steps 2, 3 | Needs Creation | Category label → { database_id, required_fields, optional_fields, default_values } |
| **Master Intake Database** | Notion database serving as the audit trail and routing status tracker | Steps 1b, 4 | Needs Creation | Properties: Title, Category (select), Source (select: iOS Shortcut / Claude Skill / Manual), Status (select: Pending / Routed / Needs Sorting / Failed), Topic Link (URL), Confidence (number), Timestamp (created_time) |
| **Topic Databases** | Individual Notion databases with category-specific schemas, one per category | Step 3 | Needs Creation | Varies per category — each has its own properties tailored to that domain. Initial categories: Shopping/Errands, Technical/Dev, Class/Study, Content/Writing, Business/Sales, Personal, Workflow/Process |
| **GAS Web App Endpoint** | Google Apps Script that receives input from iOS Shortcut, calls Claude API for classification, writes to Notion, returns confirmation | Steps 1-5 (Shortcut path) | Needs Creation | HTTP POST handler, Claude API integration (classification call), Notion API integration (create pages, update pages), error handling with fallback logging, notification response formatting |
| **Claude API Key** | Anthropic API key stored securely in GAS script properties for classification calls | Step 2 (Shortcut path) | Needs Verification | Key with sufficient quota for classification calls; stored in GAS PropertiesService, never exposed client-side |
| **Notion API Token** | Integration token with write access to master database and all topic databases | Steps 1b, 3, 4 | Needs Verification | Existing token from Open Question Logger may work if scoped broadly enough; verify permissions cover new databases |
| **iOS Shortcut** | Captures text input, sends to GAS endpoint, displays confirmation notification | Steps 1, 5 | Needs Creation | Text input field, optional urgency picker, HTTP POST action to GAS URL, parse JSON response, show notification |
| **Claude Skill** | Skill file for Claude Code / Cowork that handles conversational capture with inline classification and Notion MCP writes | Steps 1-5 (Skill path) | Needs Creation | Trigger phrases ("log a task", "log a to-do"), classification logic (inline, no API call needed), Notion MCP database writes, confirmation format, category definitions (shared with Classification Prompt) |
| **Notification Templates** | Response formats per source channel for Step 5 confirmation | Step 5 | Needs Creation | iOS: one-line push format. Claude: conversational template. Needs Sorting: explicit flag format. Error: graceful failure message. |
| **Fallback Log (Google Sheets)** | Backup destination if Notion API fails, ensuring no captured task is lost | Steps 1b, 3 (failure path) | Needs Creation | Spreadsheet with columns matching master database fields; reviewed periodically and reconciled |
