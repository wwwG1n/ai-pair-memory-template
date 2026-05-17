# Workspace Instructions

This project uses `AI_CONTEXT.md` as long-lived project memory and `.ai-pair/` as active shared workflow memory.

## Start Of Session

Before doing substantive work:

1. Read `AI_CONTEXT.md`.
2. Read `.ai-pair/status.json`.
3. Read `.ai-pair/current_handoff.md`.
4. If present, read `.ai-pair/task_board.md`, `.ai-pair/review_findings.md`, and `.ai-pair/blockers.md`.

## Default Workflow Roles

- Cursor strong model:
  - planning
  - OpenSpec gating
  - review
- Kimi extension:
  - execution
  - fix passes

Do not collapse these roles unless the human explicitly asks you to.

## Shared Memory Rules

- Treat `AI_CONTEXT.md` as the long-lived journal.
- Treat `.ai-pair/` as the source of truth for the active change.
- Prefer using the shared-memory MCP server when available.
- If MCP is unavailable, update the files directly and keep them consistent.
- Do not invent task completion, review results, blockers, or test outcomes.

## OpenSpec Gate

Use OpenSpec before implementation when any of the following are true:

- The change adds a new feature or capability.
- The change touches API, schema, contract, auth, or security behavior.
- The change spans more than 3 production files.
- The implementation is expected to take more than 45 minutes.

## End Of Each Meaningful Round

Before ending a meaningful round:

1. Refresh `AI_CONTEXT.md`.
2. Refresh `.ai-pair/status.json`.
3. Update `.ai-pair/current_handoff.md` if ownership or next action changed.
4. Append a structured event to `.ai-pair/events.jsonl`.

Keep updates concise and operational.
