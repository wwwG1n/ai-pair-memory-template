# Workflow

## Default Flow

1. The assistant that receives the request first becomes the primary assistant for that change.
2. The primary assistant reads `AGENTS.md`, `AI_CONTEXT.md`, the newest `COLDSTART_HANDOFF_*.md` when present, and `.ai-pair/current_handoff.md`.
3. The primary assistant decides whether the OpenSpec gate is required.
4. The primary assistant writes the plan or OpenSpec proposal.
5. Ownership moves to `secondary_execute`.
6. The secondary assistant executes only the approved tasks.
7. Ownership moves to `primary_review`.
8. The primary assistant reviews the diff, tests, and security posture.
9. If findings exist, ownership moves to `secondary_fix`.
10. The secondary assistant fixes only the recorded findings.
11. The primary assistant performs the final review and closes the loop.

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

Primary assistant responsibilities:

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
- a "If the primary assistant implemented this itself" execution blueprint

The primary assistant must not do the main implementation during this phase unless the human explicitly reassigns execution.

## Execution Phase

Secondary assistant responsibilities:

- read shared memory before starting
- follow `.ai-pair/task_board.md` or OpenSpec `tasks.md`
- append events and blockers
- refresh durable memory if execution materially changes project understanding
- avoid replanning unless the handoff explicitly requests it

## Review Phase

Primary assistant responsibilities:

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
