# ai-pair-memory-template

Public template for a two-assistant coding workflow:

`Cursor strong model (plan/review) -> Kimi extension (execute/fix) -> Cursor strong model (review) -> Kimi extension (auto-fix loop)`

The template does not attempt to merge private chat histories. Instead, it creates a shared memory layer that both assistants can read and write:

- `AI_CONTEXT.md` for long-lived project memory
- `.ai-pair/` for active task state, handoffs, blockers, and review results
- a local Python MCP server for structured reads, writes, and search

## What You Get

- A shared-memory directory at `.ai-pair/`
- Cursor project rules in `.cursor/rules/`
- Cursor MCP config in `.cursor/mcp.json`
- A Python shared-memory MCP server in `tools/shared_memory_mcp/`
- OpenSpec starter structure in `spec/`
- Bootstrap docs for Cursor and Kimi

## Quick Start

1. Create a fresh repo from this template.
2. Run:

   ```powershell
   python .\scripts\bootstrap_project.py --workspace . --install-dev
   ```

3. In Cursor, open the project root. Cursor should detect:
   - `AGENTS.md`
   - `AI_CONTEXT.md`
   - `.cursor/rules/`
   - `.cursor/mcp.json` rewritten to the local `.venv` interpreter
4. In the Kimi VS Code extension, add the same MCP server described in [docs/KIMI_BOOTSTRAP.md](docs/KIMI_BOOTSTRAP.md).
5. In Kimi, run `/init` once, then open:
   - `@AGENTS.md`
   - `@AI_CONTEXT.md`
   - `@.ai-pair/current_handoff.md`

## Workflow Contract

- Cursor strong model owns planning and review.
- Kimi owns execution and fix passes.
- Both assistants must treat `.ai-pair/` and `AI_CONTEXT.md` as the source of truth.
- Medium/large changes must go through the OpenSpec gate before execution.

## Repository Layout

```text
.ai-pair/                  Active shared memory and handoff state
.cursor/rules/             Cursor rules for planning, OpenSpec gating, and review
.cursor/mcp.json           Cursor MCP config for the shared-memory server
docs/                      Workflow, bootstrap, rules, and architecture docs
scripts/bootstrap_project.py
spec/                      OpenSpec starter structure
tools/shared_memory_mcp/   Python MCP server
tests/                     Unit and integration-oriented tests
AI_CONTEXT.md              Long-lived project memory
AGENTS.md                  Cross-session project instructions
```

## Key Design Choices

- Shared state lives in files first, not hidden chat state.
- MCP adds structured access and search, but files remain the truth source.
- Kimi bootstrap is a one-time setup step, not a per-task requirement.
- `high` and `critical` review findings always block `done`.
- Design drift sends the workflow back to `planning` instead of forcing local fixes.

## Verification

After bootstrap with `--install-dev`, run:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## License

MIT
