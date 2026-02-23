# Universal Task and To-Do Capture — Requirements Summary

**Assignment:** Build a Deterministic Automated Workflow | **Module:** Design Prompt Workflows

---

## Lesson Objectives

| Objective | Status | How |
|---|---|---|
| Multi-step deterministic workflow with consistent outputs | **Met** | 6-step pipeline, 5/6 steps deterministic. Same input → same database, same record, same confirmation. Classification bounded by confidence scoring + "Needs Sorting" fallback. |
| Sequenced steps with clear input/output definitions | **Met** | Each step has explicit Data In / Data Out. Full dependency map in `WORKFLOW-DEFINITION.md`. Chain: Capture → Master Record → Classify → Route → Link → Confirm. |
| Error handling and edge case logic | **Met** | 5 failure modes with handling (Notion down → Google Sheets fallback, low confidence → Needs Sorting, missing DB → flagged routing). Every step has its own failure section. No task is ever lost. |
| Documented SOP saved to registry | **Met** | 253-line `WORKFLOW-DEFINITION.md`, registered in Notion AI Building Blocks, version-controlled on GitHub. |

---

## Deliverables

| # | Deliverable | File | Status |
|---|---|---|---|
| 1 | AI Building Block Spec | `BUILDING-BLOCK-SPEC.md` (207 lines) — Execution pattern: Skill-Powered Prompt. 6 steps classified on autonomy spectrum (4 Deterministic, 1 Semi-Autonomous, 1 Autonomous). Building blocks, tools, and skill candidates mapped per step. | **Complete** |
| 2 | Baseline Workflow Prompt + Skills | `BASELINE-PROMPT.md` (167 lines) — step-by-step instructions, classification rules, routing tables, API templates, context requirements. `SKILL.md` (255 lines) — production skill with 9 hardcoded database IDs, per-database schemas, 8 categories with examples. | **Complete** |
| 3 | Test run output | Live production system. Skill installed at `~/.claude/skills/capture-task/SKILL.md`, routing to 9 Notion databases. Iterated post-launch: added 8th category (Social/Community) after observing classification gaps in real use. | **Complete** |

---

## Review Criteria

| Criterion | Evidence |
|---|---|
| Execution pattern makes sense | Skill-Powered Prompt — tool use required (Notion API), single autonomous step doesn't need Agent, reusable logic fits Skill pattern. |
| Steps classified, blocks mapped | All 6 steps have autonomy levels, building blocks, tools/connectors, and skill candidates assigned. |
| Prompt instructions clear, context listed | Explicit API call templates, classification rules, confidence thresholds, and context requirements section. |
| Skill unambiguous | Hardcoded IDs, per-database schemas, 5 classification rules, 4 confirmation templates. Every decision path specified. |
| Run on real scenario, output usable | In daily production. Tasks classify, route, link, and confirm correctly. System iterated beyond initial test runs. |

---

## Bonus

All three completed: registered in AI Operations Registry, cross-linked to workflow definitions index, committed to `github.com/bengio777/universal-task-capture`.

---

## Why This Workflow Fits

The assignment calls for **intake processing** as a good candidate. Universal Task Capture is exactly that — a fixed-rule pipeline (category definitions, confidence thresholds, routing tables, per-database schemas) where the single AI judgment call (classification) is bounded by scoring, clarification, and a safety-net fallback.
