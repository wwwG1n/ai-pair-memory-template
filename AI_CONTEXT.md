# AI Context Journal

## Context Metadata

- Context created: 2026-05-17 00:00:00 +00:00
- Last updated: 2026-05-17 00:00:00 +00:00
- Timezone: UTC
- Workspace root: `REPLACE_WITH_PROJECT_ROOT`

## Project Background

- Name: `ai-pair-memory-template`
- Domain: shared memory workflow for Cursor and Kimi coding collaboration
- Primary goal: keep planning, execution, review, and fix context synchronized without manual chat transcript copy-paste

## Persistent Context

### Key Paths

- Shared workflow memory: `.ai-pair/`
- Cursor rules: `.cursor/rules/`
- Cursor MCP config: `.cursor/mcp.json`
- Shared memory MCP server: `tools/shared_memory_mcp/`
- Bootstrap script: `scripts/bootstrap_project.py`
- OpenSpec root: `spec/`

### Locked Decisions

- File-backed memory is the truth source.
- MCP is an access layer, not the only storage layer.
- Cursor owns planning and review.
- Kimi owns execution and fix passes.
- Medium and large changes must go through the OpenSpec gate.

### Terminology, Rules, and Formulas

- `AI_CONTEXT.md`: long-lived project memory
- `.ai-pair/status.json`: active phase and owner
- `.ai-pair/events.jsonl`: append-only shared event stream
- `.ai-pair/current_handoff.md`: next actor instructions
- `high` / `critical` finding: blocks `done`
- `design_drift`: sends flow back to `planning`

## Current State

- Current objective: initialize the template for a real project
- Current status: Bootstrap only
- Latest blockers: None recorded
- Next recommended step: Run the bootstrap script, connect Cursor and Kimi to the MCP server, and start the first planned change

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
- Files touched: `AI_CONTEXT.md`, `.ai-pair/`, `.cursor/rules/`, `.cursor/mcp.json`, `tools/shared_memory_mcp/`
- Experiment or result updates: None
- New blockers or open questions: Replace placeholder workspace root during bootstrap
