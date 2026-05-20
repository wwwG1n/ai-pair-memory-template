# Kimi Bootstrap

This template assumes Kimi runs as a VS Code extension inside Cursor and accepts a **one-time bootstrap**.

## One-Time Setup

1. Open the Kimi panel in Cursor.
2. Open the gear menu and go to `MCP Servers`.
3. Add a stdio server with:

   - Command: the same Python executable that bootstrap wrote into `.cursor/mcp.json`
   - Args: `["<workspace>/tools/shared_memory_mcp/serve.py"]`
   - Env:
     - `AI_PAIR_ROOT=<workspace>`

4. Save and test the MCP connection.
5. In the first Kimi session for the project:
   - run `/init`
   - reference `@AGENTS.md`
   - reference `@AI_CONTEXT.md`
   - reference the newest `@COLDSTART_HANDOFF_YYYYMMDD.md`
   - reference `@.ai-pair/current_handoff.md`
6. Confirm Kimi can read the MCP resources and the shared files.

## Recommended Kimi Settings

Workspace settings included in `.vscode/settings.json`:

- `kimi.autosave = true`
- `kimi.editorContext = onConversationStart`

## Daily Use

After bootstrap, Kimi should:

1. read the shared handoff and determine whether Kimi is acting as the primary or secondary assistant for this change
2. read the durable cold-start handoff when it changed
3. read the task source
4. execute only the current tasks
5. write blockers and events instead of rewriting the plan

## If MCP Is Unavailable

Kimi can still operate by reading and writing the shared files directly, but it loses structured search and handoff generation from the shared MCP layer.
