# Workspace Instructions

This project uses `AI_CONTEXT.md` as compact long-lived memory, the newest `COLDSTART_HANDOFF_*.md` as the detailed recovery pack, and `.ai-pair/` as active shared workflow memory.

## Start Of Session

Before doing substantive work:

1. Read `AI_CONTEXT.md`.
2. Read the newest `COLDSTART_HANDOFF_*.md` if one exists.
3. Read `.ai-pair/status.json`.
4. Read `.ai-pair/plan.md`.
5. Read `.ai-pair/current_handoff.md`.
6. If present, read `.ai-pair/task_board.md`, `.ai-pair/review_findings.md`, and `.ai-pair/blockers.md`.

## Default Workflow Roles

- Primary assistant for the current change:
  - planning
  - OpenSpec gating
  - review
- Secondary assistant for the current change:
  - execution
  - fix passes

The primary assistant is whichever assistant receives the request first and is chosen to handle planning/review for that change.
The secondary assistant is the paired assistant that handles execution/fix for that change.

Do not collapse these roles unless the human explicitly asks you to.

## Planning Quality Bar

- Planning outputs must be detailed enough that the primary assistant could execute the task itself without inventing missing steps.
- For lightweight changes, planning must be written into `.ai-pair/plan.md`.
- For medium and large changes, planning must be written into OpenSpec proposal/tasks files and summarized in `.ai-pair/plan.md`.
- Every substantial plan should include:
  - the requested outcome and non-goals
  - the files or modules expected to change
  - the exact implementation order
  - the validation and test steps
  - open risks, ambiguities, or required approvals
  - a "If the primary assistant implemented this itself" execution blueprint

## Shared Memory Rules

- Treat `AI_CONTEXT.md` as the compact working journal.
- Treat the newest `COLDSTART_HANDOFF_*.md` as the detailed recovery handoff.
- Treat `.ai-pair/` as the source of truth for the active change.
- Treat `.ai-pair/plan.md` as the required plan artifact for lightweight changes.
- Prefer using the shared-memory MCP server when available.
- If MCP is unavailable, update the files directly and keep them consistent.
- Do not invent task completion, review results, blockers, or test outcomes.
- If `status.json` says `execution_gate` is `plan_then_handoff`, the primary assistant must stop after writing the plan and handing ownership to the secondary assistant.

## OpenSpec Gate

Use OpenSpec before implementation when any of the following are true:

- The change adds a new feature or capability.
- The change touches API, schema, contract, auth, or security behavior.
- The change spans more than 3 production files.
- The implementation is expected to take more than 45 minutes.

## End Of Each Meaningful Round

Before ending a meaningful round:

1. Refresh `AI_CONTEXT.md`.
2. Refresh the newest `COLDSTART_HANDOFF_*.md` too unless the exchange was truly trivial.
3. Refresh `.ai-pair/status.json`.
4. Refresh `.ai-pair/plan.md` when the plan changed.
5. Update `.ai-pair/current_handoff.md` if ownership or next action changed.
6. Append a structured event to `.ai-pair/events.jsonl`.

Keep updates concise and operational.
