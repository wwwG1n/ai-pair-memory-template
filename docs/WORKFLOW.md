# Workflow

## Default Flow

1. Cursor's built-in Claude reads `AGENTS.md`, `AI_CONTEXT.md`, the newest `COLDSTART_HANDOFF_*.md` when present, and `.ai-pair/current_handoff.md`.
2. Claude decides whether the OpenSpec gate is required.
3. Claude writes the plan or OpenSpec proposal.
4. Ownership moves to `kimi_execute`.
5. Kimi executes only the approved tasks.
6. Ownership moves to `claude_review`.
7. Claude reviews the diff, tests, and security posture.
8. If findings exist, ownership moves to `kimi_fix`.
9. Kimi fixes only the recorded findings.
10. Claude performs the final review and closes the loop.

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

Claude responsibilities:

- explicit startup skill routing via `using-superpowers`
- architecture and strategy review using `best-minds` when tradeoffs are non-obvious
- write a detailed plan that is executable without hidden assumptions
- update `.ai-pair/status.json`
- update `.ai-pair/task_board.md`
- update `.ai-pair/current_handoff.md`
- refresh durable memory when the round materially changes project understanding

Every substantial plan must include:

- intended outcome and non-goals
- files or modules expected to change
- concrete implementation order
- validation and test steps
- risks, ambiguities, and approvals needed
- a "If Claude implemented this itself" execution blueprint

Claude must not do the main implementation during this phase.

## Execution Phase

Kimi responsibilities:

- read shared memory before starting
- follow `.ai-pair/task_board.md` or OpenSpec `tasks.md`
- append events and blockers
- refresh durable memory if execution materially changes project understanding
- avoid replanning unless the handoff explicitly requests it

## Review Phase

Claude responsibilities:

- read diff, test output, and shared memory
- apply `pr-reviewer`
- apply `review-plan-implementation` when there is a plan or OpenSpec task list
- apply a `best-minds` security pass on security-sensitive changes
- record findings in `.ai-pair/review_findings.md`
- refresh durable memory when review changes the next safe recovery step

## Fix Loop

The shared-memory sidecar decides the next phase from review findings:

- any `design_drift` finding returns to `planning`
- any other open finding returns to `fix_pending`
- no open findings allows `done`

`high` and `critical` findings always block completion.
