# Workflow

## Default Flow

1. Cursor reads `AGENTS.md`, `AI_CONTEXT.md`, and `.ai-pair/current_handoff.md`.
2. Cursor decides whether the OpenSpec gate is required.
3. Cursor writes the plan or OpenSpec proposal.
4. Ownership moves to `kimi_execute`.
5. Kimi executes only the approved tasks.
6. Ownership moves to `cursor_review`.
7. Cursor reviews the diff, tests, and security posture.
8. If findings exist, ownership moves to `kimi_fix`.
9. Kimi fixes only the recorded findings.
10. Cursor performs the final review and closes the loop.

## OpenSpec Gate

OpenSpec is mandatory when any of the following are true:

- new feature or new capability
- API, schema, contract, auth, or security change
- more than 3 production files touched
- estimated implementation time exceeds 45 minutes

Required skills in this phase:

- `openspec-context-loading`
- `openspec-proposal-creation`

## Planning Phase

Cursor responsibilities:

- explicit startup skill routing via `using-superpowers`
- architecture and strategy review using `best-minds` when tradeoffs are non-obvious
- update `.ai-pair/status.json`
- update `.ai-pair/task_board.md`
- update `.ai-pair/current_handoff.md`

Cursor must not do the main implementation during this phase.

## Execution Phase

Kimi responsibilities:

- read shared memory before starting
- follow `.ai-pair/task_board.md` or OpenSpec `tasks.md`
- append events and blockers
- avoid replanning unless the handoff explicitly requests it

## Review Phase

Cursor responsibilities:

- read diff, test output, and shared memory
- apply `pr-reviewer`
- apply `review-plan-implementation` when there is a plan or OpenSpec task list
- apply a `best-minds` security pass on security-sensitive changes
- record findings in `.ai-pair/review_findings.md`

## Fix Loop

The shared-memory sidecar decides the next phase from review findings:

- any `design_drift` finding returns to `planning`
- any other open finding returns to `fix_pending`
- no open findings allows `done`

`high` and `critical` findings always block completion.
