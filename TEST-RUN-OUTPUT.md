# Test Run Output: Universal Task and To-Do Capture

**Date:** 2026-02-22
**Skill:** `capture-task` (installed at `~/.claude/skills/capture-task/SKILL.md`)
**Execution Pattern:** Skill-Powered Prompt
**Environment:** Claude Code with Notion MCP

---

## Test 1: Clear single-category (Class / Study)

**Input:**

> Get up to date on project submissions for HOAI Class

**Expected Category:** Class / Study
**Actual Category:** Class / Study
**Confidence:** High

**Master Record Created:**
- Page ID: `310fb3a7-cad4-815e-bcae-db03fe465a10`
- Status: Pending → Routed

**Topic Database Entry:**
- Database: Study To-Dos (`3c36c983-099b-48e5-9484-5b878bdd95bb`)
- Page URL: https://www.notion.so/310fb3a7cad481469451d5dc708b7f3f
- Properties set: Task, Priority (Medium), Status (To Do), Class (Hands-on AI), Topic (Project submissions)

**Master Record Updated:**
- Status: Routed
- Category: Class / Study
- Topic Link: https://www.notion.so/310fb3a7cad481469451d5dc708b7f3f
- Confidence: High

**Confirmation Message:**

> Logged to Class / Study: "Get up to date on project submissions for HOAI Class"

**Result:** Pass

---

## Test 2: Different domain (Shopping / Errands)

**Input:**

> Go to storage unit and get rid of unnecessary items with a truck

**Expected Category:** Shopping / Errands
**Actual Category:** Shopping / Errands
**Confidence:** High

**Master Record Created:**
- Page ID: `310fb3a7-cad4-8115-aa9f-cf9f0024b461`
- Status: Pending → Routed

**Topic Database Entry:**
- Database: Shopping & Errands (`4601cd6c-0145-43bb-842f-5aa0ea21e3f2`)
- Page URL: https://www.notion.so/310fb3a7cad481728e98f5db483a4f40
- Properties set: Task, Priority (Medium), Status (To Do), Location (Storage unit), Notes (Need a truck. Sort and dispose of unnecessary items.)

**Master Record Updated:**
- Status: Routed
- Category: Shopping / Errands
- Topic Link: https://www.notion.so/310fb3a7cad481728e98f5db483a4f40
- Confidence: High

**Confirmation Message:**

> Logged to Shopping / Errands: "Go to storage unit and get rid of unnecessary items with a truck"

**Result:** Pass

---

## Test 3: Concurrent multi-task capture (same category)

**Use Case:** User provides two tasks in a single message. The workflow handles both through the full pipeline concurrently — parallel master record creation, parallel classification, parallel routing, parallel linking.

**Input:**

> Go to storage unit and pick up the following items: Mixer, Bike, File dividers, Ottoman
> Pick up ingredients for pine nut cookies from Sprouts: Almond flour, Pine nuts, Eggs

### Task A: Storage unit pickup

**Expected Category:** Shopping / Errands
**Actual Category:** Shopping / Errands
**Confidence:** High

**Master Record Created:**
- Page ID: `310fb3a7-cad4-818e-bb8b-f1020bce5914`
- Status: Pending → Routed

**Topic Database Entry:**
- Database: Shopping & Errands (`4601cd6c-0145-43bb-842f-5aa0ea21e3f2`)
- Page URL: https://www.notion.so/310fb3a7cad4818b9374fe7814c465af
- Properties set: Task, Priority (Medium), Status (To Do), Location (Storage unit), Notes (Items to pick up: Mixer, Bike, File dividers, Ottoman)

### Task B: Sprouts grocery run

**Expected Category:** Shopping / Errands
**Actual Category:** Shopping / Errands
**Confidence:** High

**Master Record Created:**
- Page ID: `310fb3a7-cad4-8161-b28c-e19d40a79dc9`
- Status: Pending → Routed

**Topic Database Entry:**
- Database: Shopping & Errands (`4601cd6c-0145-43bb-842f-5aa0ea21e3f2`)
- Page URL: https://www.notion.so/310fb3a7cad4814cb005e80e1a3a41c7
- Properties set: Task, Priority (Medium), Status (To Do), Location (Sprouts), Notes (Shopping list: Almond flour, Pine nuts, Eggs)

### Concurrency Notes

- **Master records:** Both created in a single Notion API call (batch)
- **Topic entries:** Both created in a single Notion API call (batch)
- **Master linking:** Both updated in parallel (concurrent API calls)
- **Classification:** Both classified independently to Shopping / Errands — same category, separate entries
- **No data collision:** Each task gets its own master record + topic entry with distinct page IDs

**Result:** Pass

---

## Test 4: Edge case — ambiguous input triggers clarification

**Input:**

> Research competitors for the pitch deck

**Expected Behavior:** Classification is ambiguous between Business / Sales and Content / Writing. The skill should ask a clarifying question before routing.
**Actual Behavior:** Skill correctly identified the ambiguity and asked: "Should I file this under **Business / Sales** (pitch prep for a deal) or **Content / Writing** (research and writing task)?" When no clarification was provided, the task was routed to Needs Sorting — the documented fallback behavior.

**Master Record Created:**
- Page ID: `310fb3a7-cad4-81d7-b130-ebfd4d29a2fc`
- Status: Pending → Needs Sorting

**Topic Database Entry:**
- Database: Needs Sorting (`f1a5fa34-3113-4212-b12c-1c1a5fa58955`)
- Page URL: https://www.notion.so/310fb3a7cad4815d925cee0a3dfc9dd3
- Properties set: Task, Status (Unsorted), Suggested Category (Business / Sales), Reason (Ambiguous — clarification requested but not provided)

**Master Record Updated:**
- Status: Needs Sorting
- Category: Needs Sorting
- Topic Link: https://www.notion.so/310fb3a7cad4815d925cee0a3dfc9dd3
- Confidence: Low

**Confirmation Message:**

> Captured "Research competitors for the pitch deck" but couldn't classify confidently — added to Needs Sorting.

**Result:** Pass — clarification path and Needs Sorting fallback both worked as designed.

---

## Summary

| Test | Input | Category | Behavior Tested | Result |
|------|-------|----------|----------------|--------|
| 1 | Get up to date on project submissions for HOAI Class | Class / Study | Clear single-category classification | Pass |
| 2 | Go to storage unit and get rid of unnecessary items with a truck | Shopping / Errands | Different domain, location extraction | Pass |
| 3 | Two tasks: storage unit pickup + Sprouts grocery run | Shopping / Errands (both) | Concurrent multi-task capture (batch API calls, parallel linking) | Pass |
| 4 | Research competitors for the pitch deck | Needs Sorting | Ambiguous input → clarification question → fallback to Needs Sorting | Pass |

**Overall:** 4 of 4 tests passed.

---

## Observations

- **Classification accuracy:** 3 of 4 tasks classified immediately with high confidence. The 4th correctly triggered the ambiguity path.
- **Concurrency:** Batch Notion API calls handled multi-task input without data collision. Each task got its own master record and topic entry.
- **Edge case handling:** The Needs Sorting fallback preserved the task with a suggested category and reasoning, so nothing was lost.
- **Iteration evidence:** The system has been refined since initial build — expanded from 7 to 8 categories (Social/Community added post-launch) and the skill was upgraded from the baseline prompt to production with per-database schema templates.
