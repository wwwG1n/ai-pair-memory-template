# ai-pair-memory-template

Public template for a two-assistant coding workflow:

`Primary assistant (plan/review) -> secondary assistant (execute/fix) -> primary assistant (review) -> secondary assistant (auto-fix loop)`

The template does not attempt to merge private chat histories. Instead, it creates a shared memory layer that both assistants can read and write:

- `AI_CONTEXT.md` for compact long-lived project memory
- the newest `COLDSTART_HANDOFF_YYYYMMDD.md` for detailed cold-start recovery
- `.ai-pair/` for active task state, handoffs, blockers, and review results
- a local Python MCP server for structured reads, writes, and search

## What You Get

- A shared-memory directory at `.ai-pair/`
- A `COLDSTART_HANDOFF_YYYYMMDD.md` file created during bootstrap
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
   - the newest `COLDSTART_HANDOFF_YYYYMMDD.md`
   - `.cursor/rules/`
   - `.cursor/mcp.json` rewritten to the local `.venv` interpreter
4. In the Kimi VS Code extension, add the same MCP server described in [docs/KIMI_BOOTSTRAP.md](docs/KIMI_BOOTSTRAP.md).
5. In Kimi, run `/init` once, then open:
   - `@AGENTS.md`
   - `@AI_CONTEXT.md`
   - the newest `@COLDSTART_HANDOFF_YYYYMMDD.md`
   - `@.ai-pair/current_handoff.md`

At the start of each change, send the request to whichever assistant you want to act as the strong-model lane for that change.
That first request recipient becomes the `primary` assistant; the other assistant becomes the `secondary` assistant.

## Workflow Contract

- The primary assistant owns planning and review for the current change.
- The secondary assistant owns execution and fix passes for the current change.
- The primary assistant is whichever assistant received the request first and was chosen to handle planning/review.
- Both assistants must treat `AI_CONTEXT.md`, the newest `COLDSTART_HANDOFF_*.md`, and `.ai-pair/` as the source of truth for their respective scopes.
- Medium/large changes must go through the OpenSpec gate before execution.
- The primary assistant's plan must be detailed enough that the primary assistant itself could execute the task step by step without filling in missing implementation details.

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
AI_CONTEXT.md              Compact long-lived project memory
COLDSTART_HANDOFF_*.md    Detailed cold-start recovery pack
AGENTS.md                  Cross-session project instructions
```

## Key Design Choices

- Shared state lives in files first, not hidden chat state.
- Durable memory follows the local `context-coldstart-pack` dual-file pattern.
- MCP adds structured access and search, but files remain the truth source.
- Plans are intentionally detailed and include a self-execution blueprint for the primary assistant.
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
