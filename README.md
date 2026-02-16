# Universal Task and To-Do Capture

Capture any task or to-do from any interface, classify it by topic using AI, and route it to the correct Notion database.

## Status

- **Claude Skill (Phase 1):** In Production
- **iOS Shortcut + GAS (Phase 2):** Iceboxed

## Architecture

Master intake database as audit trail + routing hub, with 8 topic-specific databases and a Needs Sorting fallback.

| Component | Location |
|-----------|----------|
| Skill | [`~/.claude/skills/capture-task/SKILL.md`](https://github.com/bengio777/agent-skills/tree/main/capture-task) |
| Workflow Definition | `WORKFLOW-DEFINITION.md` |
| Building Block Spec | `BUILDING-BLOCK-SPEC.md` |
| Baseline Prompt | `BASELINE-PROMPT.md` |
| Notion Databases | 10 databases under Universal Task Capture parent page |

## Topic Databases

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
| (fallback) | Needs Sorting |

## How It Works

1. **Capture** — Receive task via trigger phrase ("log a task", "log a to-do")
2. **Master Record** — Create audit trail entry with status "Pending"
3. **Classify** — LLM determines topic category (8 categories + Needs Sorting)
4. **Route** — Create entry in the matched topic database
5. **Link** — Update master record with category and topic link
6. **Confirm** — Brief confirmation to user

## Trigger Phrases

- "log a task", "log a to-do", "capture this", "add a task"
- "I need to remember to...", "remind me to...", "add to my list"
- "what tasks do I have", "show my tasks", "check my intake"
