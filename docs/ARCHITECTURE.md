# Architecture

## Goal

Keep Cursor and Kimi aligned without copying private chat transcripts between panels.

## Core Principle

The system does not synchronize hidden conversation state. It synchronizes **durable workflow state** instead.

That state is split into three layers:

- `AI_CONTEXT.md`: compact long-lived project memory
- the newest `COLDSTART_HANDOFF_*.md`: detailed cold-start recovery memory
- `.ai-pair/`: active execution and review memory

## Components

### 1. File Truth Layer

The following files are the canonical state:

- `COLDSTART_HANDOFF_*.md`
- `.ai-pair/status.json`
- `.ai-pair/events.jsonl`
- `.ai-pair/task_board.md`
- `.ai-pair/current_handoff.md`
- `.ai-pair/review_findings.md`
- `.ai-pair/blockers.md`
- `AI_CONTEXT.md`

Both assistants must treat these files as authoritative, with `AI_CONTEXT.md` and the newest handoff carrying durable project memory and `.ai-pair/` carrying active change state.

### 2. MCP Access Layer

The Python server in `tools/shared_memory_mcp/` exposes:

- Resources:
  - `context://current`
  - `tasks://open`
  - `handoff://latest`
  - `review://open-findings`
- Tools:
  - `append_event`
  - `update_status`
  - `render_handoff`
  - `record_review`
  - `search_events`

The MCP server improves structure and retrieval, but does not replace the files.

### 3. Cursor Control Layer

Cursor rules live in `.cursor/rules/` and enforce:

- startup memory loading
- skill routing
- OpenSpec gating
- review loop discipline

### 4. Kimi Execution Layer

Kimi uses the same files and the same MCP server.

Kimi is intentionally limited to execution and fix passes. It should not silently replace planning or review ownership.

## Ownership Model

- `codex_plan`: produces plans and OpenSpec proposals
- `kimi_execute`: implements approved tasks
- `codex_review`: reviews diffs, tests, and security risks
- `kimi_fix`: addresses review findings

## Phase Model

Valid phases:

- `planning`
- `approved`
- `executing`
- `review_pending`
- `fix_pending`
- `done`

## Why File-Backed Memory Wins

- It survives new tabs and new sessions.
- It is visible and auditable.
- It degrades gracefully if MCP is temporarily unavailable.
- It works across tools that do not share internal chat memory.
