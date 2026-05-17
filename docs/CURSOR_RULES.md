# Cursor Rules

## Rule Set

### `00-bootstrap.mdc`

Always applies.

Purpose:

- load `AGENTS.md`
- load `AI_CONTEXT.md`
- load active shared-memory files
- enforce `using-superpowers` startup discipline

### `10-planning.mdc`

Planning-only rule.

Purpose:

- keep Cursor in planning mode
- call `best-minds` for non-obvious architecture and safety tradeoffs
- update handoff and task state

### `20-openspec-gate.mdc`

Medium and large change gate.

Purpose:

- force explicit OpenSpec usage
- call `openspec-context-loading`
- call `openspec-proposal-creation`

### `30-review-loop.mdc`

Review-only rule.

Purpose:

- call `pr-reviewer`
- call `review-plan-implementation`
- call `best-minds` on security-sensitive diffs
- block `done` on severe findings

## Editing Guidance

- Keep bootstrap rules small and stable.
- Put project-specific logic in nested `.cursor/rules/` directories if the repo later grows multiple subsystems.
- Do not add rules that let Cursor silently take over Kimi's execution role.
