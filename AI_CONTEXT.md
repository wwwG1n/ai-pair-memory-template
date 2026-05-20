# AI Context Journal

## Context Metadata

- Context created: 2026-05-17 00:00:00 +00:00
- Last updated: 2026-05-20 20:24:00 +08:00
- Timezone: UTC
- Workspace root: `REPLACE_WITH_PROJECT_ROOT`

## Project Background

- Name: `ai-pair-memory-template`
- Domain: shared memory workflow for Cursor and Kimi coding collaboration
- Primary goal: keep planning, execution, review, and fix context synchronized without manual chat transcript copy-paste

## Persistent Context

### Key Paths

- Shared workflow memory: `.ai-pair/`
- Detailed recovery handoff: newest `COLDSTART_HANDOFF_*.md`
- Cursor rules: `.cursor/rules/`
- Cursor MCP config: `.cursor/mcp.json`
- Shared memory MCP server: `tools/shared_memory_mcp/`
- Bootstrap script: `scripts/bootstrap_project.py`
- OpenSpec root: `spec/`

### Locked Decisions

- File-backed memory is the truth source.
- Durable memory follows the local `context-coldstart-pack` dual-file pattern.
- MCP is an access layer, not the only storage layer.
- The assistant that receives the request first becomes the primary assistant for that change and owns planning/review.
- The paired assistant becomes the secondary assistant for that change and owns execution/fix passes.
- Medium and large changes must go through the OpenSpec gate.

### Terminology, Rules, and Formulas

- `AI_CONTEXT.md`: compact long-lived project memory
- `.ai-pair/status.json`: active phase and owner
- `.ai-pair/events.jsonl`: append-only shared event stream
- `.ai-pair/current_handoff.md`: next actor instructions
- `high` / `critical` finding: blocks `done`
- `design_drift`: sends flow back to `planning`

## Current State

- Current objective: initialize the template for a real project
- Current status: Bootstrap only
- Latest blockers: None recorded
- Next recommended step: Run the bootstrap script, connect both assistants to the MCP server, assign the first request recipient as the primary assistant, and verify that the primary assistant stops after writing `.ai-pair/plan.md` and handing ownership to `secondary_execute`

## Experiments Snapshot

- Current or latest experiment: Not run in this session
- Configs: None
- Commands: None
- Hyperparameters: None
- Checkpoints or outputs: None
- Results: None
- Interpretation: This template is for workflow state, not model benchmarking

## Round Log

### 2026-05-17 00:00:00 +00:00

- User request: Bootstrapped the template
- New decisions or changes: Initialized long-lived memory and shared workflow memory layout
- Files touched: `AI_CONTEXT.md`, the newest `COLDSTART_HANDOFF_*.md`, `.ai-pair/`, `.cursor/rules/`, `.cursor/mcp.json`, `tools/shared_memory_mcp/`
- Experiment or result updates: None
- New blockers or open questions: Replace placeholder workspace root during bootstrap

### 2026-05-19 00:00:09 +08:00

- User request: Asked to replace the strong-model role with the Codex plugin inside Cursor and publish the update
- New decisions or changes: Renamed the planning/review role from generic Cursor strong-model wording to explicit Codex-in-Cursor ownership across docs, bootstrap templates, shared-memory owner ids, and review-loop routing
- Files touched: `README.md`, `AGENTS.md`, `AI_CONTEXT.md`, the newest `COLDSTART_HANDOFF_*.md`, `.ai-pair/`, `.cursor/rules/`, `docs/`, `scripts/bootstrap_project.py`, `spec/specs/shared-memory-workflow/spec.md`, `tools/shared_memory_mcp/shared_memory_mcp/service.py`, and `tests/`
- Experiment or result updates: `python -m pytest` passed after the owner rename and workflow copy update
- New blockers or open questions: None recorded

### 2026-05-19 00:04:11 +08:00

- User request: Asked to sync the local `context-coldstart-pack` updates into this workflow before publishing
- New decisions or changes: Upgraded the template from single-file durable memory to the local dual-file pattern: `AI_CONTEXT.md` as compact memory plus the newest `COLDSTART_HANDOFF_*.md` as the detailed recovery pack, while keeping `.ai-pair/` as active shared execution state. Updated bootstrap so it creates the first cold-start handoff automatically, and aligned `AGENTS.md`, Cursor rules, workflow docs, and Kimi bootstrap guidance with that model
- Files touched: `AGENTS.md`, `AI_CONTEXT.md`, `README.md`, `.cursor/rules/00-bootstrap.mdc`, `docs/`, `scripts/bootstrap_project.py`, and `tests/test_bootstrap_project.py`
- Experiment or result updates: `python -m pytest` still passed after the dual-memory sync
- New blockers or open questions: None recorded

### 2026-05-19 00:31:42 +08:00

- User request: Asked to update the workflow again so the strong-model role is Cursor's built-in Claude instead of Codex, and to require more detailed plans that include how the strong model would execute the task itself
- New decisions or changes: Renamed the strong-model role from Codex to Claude across workflow docs, default shared-memory files, bootstrap output, routing owner ids, and tests. Tightened the planning contract so substantial plans must now include scope, concrete files, implementation order, validation steps, risks, and an explicit "If Claude implemented this itself" execution blueprint
- Files touched: `AGENTS.md`, `README.md`, `.ai-pair/*`, `.cursor/rules/10-planning.mdc`, `.cursor/rules/20-openspec-gate.mdc`, `.cursor/rules/30-review-loop.mdc`, `docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, `docs/CURSOR_RULES.md`, `docs/KIMI_BOOTSTRAP.md`, `scripts/bootstrap_project.py`, `tools/shared_memory_mcp/shared_memory_mcp/service.py`, `spec/specs/shared-memory-workflow/spec.md`, and `tests/*`
- Experiment or result updates: Template validation should still pass through `python -m pytest` after the Claude rename and planning-detail upgrades
- New blockers or open questions: None recorded

### 2026-05-20 00:08:00 +08:00

- User request: Asked to stop pre-binding strong and weak roles to fixed models, and then asked to update the published template so whoever receives the request first becomes the strong-model lane for that change
- New decisions or changes: Refactored the workflow from model-bound ownership to role-bound ownership. Shared-memory owners now use `primary_plan`, `primary_review`, `secondary_execute`, and `secondary_fix`. The primary assistant is defined as whichever assistant first receives the request and handles planning/review for that change; the paired assistant becomes the secondary lane for execution/fix
- Files touched: `AGENTS.md`, `README.md`, `.ai-pair/*`, `.cursor/rules/*.mdc`, `docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, `docs/CURSOR_RULES.md`, `docs/KIMI_BOOTSTRAP.md`, `scripts/bootstrap_project.py`, `tools/shared_memory_mcp/shared_memory_mcp/service.py`, `spec/specs/shared-memory-workflow/spec.md`, and `tests/*`
- Experiment or result updates: `python -m pytest` passed after the role-driven owner refactor
- New blockers or open questions: None recorded

### 2026-05-20 20:24:00 +08:00

- User request: Reported that the workflow still allowed the primary assistant to continue editing code after generating a plan, and asked for the plan stage to stop as intended
- New decisions or changes: Added a harder execution gate. The template now introduces `.ai-pair/plan.md` as a required plan artifact for lightweight changes, stores `execution_gate: plan_then_handoff` in `.ai-pair/status.json`, updates bootstrap defaults accordingly, and strengthens AGENTS/rules/docs so the primary assistant must stop after writing the plan and handing ownership to `secondary_execute` unless the human explicitly overrides the gate
- Files touched: `AGENTS.md`, `README.md`, `.ai-pair/plan.md`, `.ai-pair/status.json`, `.ai-pair/current_handoff.md`, `.ai-pair/task_board.md`, `.cursor/rules/10-planning.mdc`, `docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, `docs/CURSOR_RULES.md`, `scripts/bootstrap_project.py`, `tools/shared_memory_mcp/shared_memory_mcp/models.py`, `tools/shared_memory_mcp/shared_memory_mcp/store.py`, `tests/test_bootstrap_project.py`, and `tests/test_shared_memory_service.py`
- Experiment or result updates: `python -m pytest` passed after the hard-stop execution-gate update
- New blockers or open questions: None recorded
