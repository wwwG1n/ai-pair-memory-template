# Shared Memory Workflow Specification

## Capability

The repository SHALL provide a file-backed shared memory layer so planning, execution, review, and fix context survive new chats and new sessions.

### Requirement: Shared Active Workflow Memory

WHEN an assistant begins substantive work,
the system SHALL expose the active shared workflow state through `.ai-pair/`.

#### Scenario: Read current phase and handoff
GIVEN a project using this template
WHEN an assistant reads `.ai-pair/status.json` and `.ai-pair/current_handoff.md`
THEN the assistant can determine the current phase and current owner

### Requirement: Review Findings Control Phase Routing

WHEN a review is recorded,
the system SHALL update the next workflow phase based on the open findings.

#### Scenario: Open finding requires fix pass
GIVEN a recorded review with an open defect finding
WHEN the shared-memory service processes the review
THEN the next phase becomes `fix_pending`
AND the next owner becomes `secondary_fix`

#### Scenario: Design drift requires replanning
GIVEN a recorded review with an open `design_drift` finding
WHEN the shared-memory service processes the review
THEN the next phase becomes `planning`
AND the next owner becomes `primary_plan`

### Requirement: Severe Findings Block Completion

WHEN any open finding has severity `high` or `critical`,
the system SHALL prevent the workflow from reaching `done`.

#### Scenario: High severity finding blocks completion
GIVEN a review containing an open `high` severity finding
WHEN the next phase is computed
THEN the system does not set the phase to `done`
