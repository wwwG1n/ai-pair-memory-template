# Current Handoff

## Owner

- Current owner: `primary_plan`
- Owner meaning: This belongs to the assistant that first received the request and is handling planning for the current change.
- Current phase: `planning`

## Required Action

The assistant that first received the request should do one of the following:

1. Produce a lightweight plan for a small change, or
2. Trigger the OpenSpec gate for a medium/large change

Any substantial plan should include the concrete implementation order, validation steps, and a section explaining how the primary assistant would complete the task itself if execution stayed with the strong model.

Under the default `plan_then_handoff` gate, the primary assistant must stop after writing `.ai-pair/plan.md` and switching ownership.

The secondary assistant should not start editing code until ownership moves to `secondary_execute`.
