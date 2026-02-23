# Universal Task and To-Do Capture — Assignment Requirements Mapping

**Assignment:** Build a Deterministic Automated Workflow
**Module:** Design Prompt Workflows
**Project:** Universal Task and To-Do Capture

---

## Lesson Objectives → Evidence

### 1. "Build a multi-step deterministic workflow using prompt chaining that produces consistent outputs from the same inputs"

**Met.** The workflow is a 6-step sequential pipeline where 5 of 6 steps are deterministic (lookup, write, format). The same task input with the same classification result always routes to the same database, creates the same record structure, and produces the same confirmation message. The only non-deterministic step is classification (Step 3), which is bounded by confidence scoring and a "Needs Sorting" fallback.

**Evidence:**
- `BUILDING-BLOCK-SPEC.md` — Autonomy Spectrum Summary shows 5/6 steps deterministic
- `SKILL.md` — Steps 1–6 are fixed, sequential, and rule-driven
- `BASELINE-PROMPT.md` — Each step has explicit input → output definitions

### 2. "Sequence workflow steps with clear input/output definitions between each stage"

**Met.** Every step has defined Data In and Data Out. The dependency chain is explicit: Capture → Master Record → Classify → Route → Link → Confirm.

**Evidence:**
- `WORKFLOW-DEFINITION.md` — Dependency Map table (lines 227–234) specifies what each step depends on and what it produces:

  | Step | Depends On | Produces |
  |------|-----------|----------|
  | 1: Capture | User input | Structured capture object |
  | 1b: Create Master | Step 1 output | Master record page ID |
  | 2: Classify | Step 1 output | Category + confidence |
  | 3: Route | Step 2 output + category-to-DB map | Topic page ID |
  | 4: Link | Step 1b output + Step 3 output | Updated master record |
  | 5: Confirm | Steps 2, 3, 4 outputs + source | User notification |

- `BUILDING-BLOCK-SPEC.md` — Step Sequence and Dependencies diagram (lines 118–136) with branching logic for high/low confidence paths

### 3. "Implement error handling and edge case logic to ensure reliable execution"

**Met.** Failure modes are defined per step with specific handling strategies. The system is designed so no captured task is ever lost.

**Evidence:**
- `BUILDING-BLOCK-SPEC.md` — Failure Modes table covers 5 scenarios:

  | Failure | Handling |
  |---------|----------|
  | Notion API unavailable | Log to Google Sheets fallback, master record stays "Pending" |
  | Classification confidence low | Route to Needs Sorting (Shortcut) or ask clarifying question (Claude) |
  | Unknown category returned | Route to Needs Sorting with flag for config update |
  | Topic database doesn't exist | Route to Needs Sorting with note about missing destination |
  | Schema mismatch | Create with available data, flag incomplete fields |

- `WORKFLOW-DEFINITION.md` — Each of the 6 steps has its own Failure Modes section detailing step-specific failures and recovery strategies (lines 44–46, 67, 98–101, 130–132, 156–157, 187–189)
- `SKILL.md` — Step 6 (Confirm) includes four distinct confirmation templates for: success, user-clarified, needs sorting, and partial failure (lines 223–234)

### 4. "Document the workflow SOP and save it to your registry"

**Met.** The workflow has a full SOP (Workflow Definition) and is registered in the AI Operations Registry.

**Evidence:**
- `WORKFLOW-DEFINITION.md` — 253-line SOP with scenario metadata, refined steps, decision points, context shopping list, and dependency mapping
- Skill installed and live at `~/.claude/skills/capture-task/SKILL.md` (255 lines)
- Version-controlled on GitHub: `bengio777/universal-task-capture`
- Registered in Notion AI Building Blocks database

---

## Assignment Instructions → Evidence

### Part 1: Design ("Upload your Workflow Definition and let the AI recommend an execution pattern, classify each step, and map building blocks")

**Completed.** Output saved as `BUILDING-BLOCK-SPEC.md`.

| Design Requirement | Where It Appears |
|---|---|
| Execution pattern recommendation | `BUILDING-BLOCK-SPEC.md` — "Recommended Pattern: Skill-Powered Prompt" with 5-point reasoning for why Prompt, Agent, and Multi-Agent patterns were ruled out |
| Each step classified | `BUILDING-BLOCK-SPEC.md` — Step-by-Step Decomposition table with Autonomy Level column (AI-Deterministic, AI-Semi-Autonomous, AI-Autonomous) per step |
| Building blocks mapped | `BUILDING-BLOCK-SPEC.md` — Building Block(s) and Tools/Connectors columns per step, plus Skill Candidates section with full input/output/decision logic spec |

### Part 2: Construct ("Follow the build path for your recommended execution pattern... Save the prompt output as `[name]-prompt.md`. If your pattern is Skill-Powered Prompt, also save any skill files you built.")

**Completed.** Output saved as `BASELINE-PROMPT.md` + `SKILL.md`.

| Construct Requirement | Where It Appears |
|---|---|
| Baseline Workflow Prompt | `BASELINE-PROMPT.md` — 167-line runnable prompt with step-by-step instructions, classification rules, routing tables, Notion API call templates, input/output specs, and context requirements |
| Skill files (Skill-Powered Prompt pattern) | `SKILL.md` — 255-line production skill with hardcoded database IDs for 9 topic databases, per-database schema templates, classification examples, and operational procedures for reviewing tasks and adding categories |

### Part 3: Run ("Run your workflow on a real scenario, evaluate the output, and iterate. Run at least twice.")

**Completed.** The workflow is in active daily production use.

| Run Requirement | Evidence |
|---|---|
| Run on a real scenario | Skill is installed at `~/.claude/skills/capture-task/SKILL.md` and actively used. Master Task Intake database (ID: `c20d0a8a-48eb-4556-824a-8db6d41afabd`) contains live captured tasks routed across 9 topic databases. |
| Run at least twice | The system has been iterated beyond two test runs — it expanded from 7 categories to 8 (Social/Community was added post-launch based on classification gaps observed during use), and the skill was refined from `BASELINE-PROMPT.md` into the production `SKILL.md` with per-database schema templates. |
| Output is usable without heavy editing | Tasks route to correct databases with appropriate metadata. Confirmation messages are 1–2 sentences. The "Needs Sorting" fallback handles edge cases without losing data. |

---

## Review and Refine Criteria → Evidence

### "AI Building Block Spec: Execution pattern makes sense, each step is classified, building blocks are mapped"

| Criterion | Status | Evidence |
|---|---|---|
| Execution pattern makes sense | **Yes** | Skill-Powered Prompt — justified because tool use is required (Notion API), one autonomous step (classification) doesn't warrant a full Agent, and the reusable classification + routing logic fits the Skill pattern. (`BUILDING-BLOCK-SPEC.md`, lines 5–12) |
| Each step is classified | **Yes** | 6 steps classified on the autonomy spectrum: 4 AI-Deterministic (1b, 3, 4, 5), 1 AI-Semi-Autonomous (1), 1 AI-Autonomous (2). (`BUILDING-BLOCK-SPEC.md`, lines 38–45) |
| Building blocks are mapped | **Yes** | Each step maps to specific building blocks (Skill, iOS Shortcut, GAS), tools (Notion MCP, Claude API, Notion API, Google Sheets API, iOS Shortcuts), and the single skill candidate `capture-task` is fully specified with inputs, outputs, decision logic, and failure modes. (`BUILDING-BLOCK-SPEC.md`, lines 60–113, 167–177) |

### "Baseline Workflow Prompt: Instructions are clear, context requirements are listed, output is consistent across different inputs"

| Criterion | Status | Evidence |
|---|---|---|
| Instructions are clear | **Yes** | `BASELINE-PROMPT.md` provides explicit step-by-step instructions with Notion API call templates, classification rules ("Choose the single best category. Do not multi-classify."), and confidence thresholds (≥0.8 auto-route, <0.8 clarify or flag). |
| Context requirements are listed | **Yes** | `BASELINE-PROMPT.md`, Context Requirements section (lines 145–149): category definitions, category-to-database map, master intake database ID. |
| Output is consistent across different inputs | **Yes** | Every input follows the same pipeline: capture → master record → classify → route → link → confirm. Output format is templated per confirmation type (success, clarified, needs sorting, partial failure). Category-to-database routing is deterministic lookup. |

### "Skills (if applicable): Instructions are specific enough for the AI to execute without ambiguity"

| Criterion | Status | Evidence |
|---|---|---|
| Specific enough for AI execution | **Yes** | `SKILL.md` contains: hardcoded database IDs for all 9 databases, per-database Notion API call templates with exact property names and value formats, 8 category definitions with 3–4 examples each, 5 classification rules, 4 confirmation message templates, and procedures for reviewing tasks and adding new categories. No ambiguity — every decision path is specified. |

### "Test run: You've run the workflow on at least one real scenario and the output is usable"

| Criterion | Status | Evidence |
|---|---|---|
| Run on real scenario | **Yes** | The skill is installed in production at `~/.claude/skills/capture-task/SKILL.md` and routes to live Notion databases with real task data. |
| Output is usable | **Yes** | Tasks are classified, routed to the correct topic database with domain-specific metadata, linked back to the master audit trail, and confirmed with a 1–2 sentence message. The system was iterated: an 8th category (Social/Community) was added after observing classification gaps in real use. |

---

## Deliverables Checklist

| # | Deliverable | Required Format | File | Status |
|---|---|---|---|---|
| 1 | AI Building Block Spec | `[name]-building-block-spec.md` | `BUILDING-BLOCK-SPEC.md` (207 lines) | **Complete** |
| 2 | Baseline Workflow Prompt | `[name]-prompt.md` + skill files | `BASELINE-PROMPT.md` (167 lines) + `SKILL.md` (255 lines) | **Complete** |
| 3 | Test run output | Evidence of real execution | Live production system: 9 Notion databases, active skill, iterated post-launch | **Complete** |

---

## Bonus (Optional) → Evidence

| Bonus Item | Status | Evidence |
|---|---|---|
| Register building blocks in AI Operations Registry | **Done** | Skill registered in Notion AI Building Blocks database via `registering-building-blocks` skill |
| Link back to workflow entry | **Done** | Workflow Definition (`WORKFLOW-DEFINITION.md`) cross-referenced in `Projects/workflow-definitions/` index |
| Commit `.md` files to GitHub | **Done** | All artifacts version-controlled at `github.com/bengio777/universal-task-capture` |

---

## Deterministic Workflow Fit

The assignment specifies: *"Choose one that has predictable, fixed steps — a deterministic workflow where the AI follows rules and templates rather than making open-ended judgments."*

**Good candidates listed:** recurring reports, prospecting or research workflows, template-driven content, data extraction and formatting, **intake processing**.

Universal Task Capture is **intake processing** — the exact use case the assignment calls out. The pipeline follows fixed rules (category definitions, confidence thresholds, database routing tables) and templates (per-database schemas, confirmation messages). The single AI judgment call (classification) is bounded by confidence scoring, clarification prompts, and a "Needs Sorting" safety net — making even the autonomous step predictable and debuggable.

---

## File Inventory

| File | Location | Lines | Purpose |
|---|---|---|---|
| `BUILDING-BLOCK-SPEC.md` | `Projects/universal-task-capture/` | 207 | Deliverable 1: AI Building Block Spec |
| `BASELINE-PROMPT.md` | `Projects/universal-task-capture/` | 167 | Deliverable 2: Baseline Workflow Prompt |
| `SKILL.md` | `Projects/universal-task-capture/` | 255 | Deliverable 2: Skill file (Skill-Powered Prompt pattern) |
| `WORKFLOW-DEFINITION.md` | `Projects/universal-task-capture/` | 253 | Supporting: Full SOP from Deconstruct assignment |
| `SKILL.md` (installed) | `~/.claude/skills/capture-task/` | 255 | Production deployment |
| `README.md` | `Projects/universal-task-capture/` | — | Project overview |
