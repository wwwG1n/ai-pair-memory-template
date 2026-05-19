from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HANDOFF_GLOB = "COLDSTART_HANDOFF_*.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def handoff_filename_for_today() -> str:
    return f"COLDSTART_HANDOFF_{datetime.now().strftime('%Y%m%d')}.md"


def newest_handoff_path(workspace: Path) -> Path | None:
    candidates = sorted(path for path in workspace.glob(HANDOFF_GLOB) if path.is_file())
    return candidates[-1] if candidates else None


def should_use_openspec(
    *,
    new_feature: bool,
    touches_api_or_schema: bool,
    production_files_touched: int,
    estimated_minutes: int,
) -> bool:
    return any(
        [
            new_feature,
            touches_api_or_schema,
            production_files_touched > 3,
            estimated_minutes > 45,
        ]
    )


def render_kimi_stdio_config(workspace: Path) -> dict[str, object]:
    python_bin = detect_python_bin(workspace)
    return {
        "command": str(python_bin),
        "args": [str(workspace / "tools" / "shared_memory_mcp" / "serve.py")],
        "env": {
            "AI_PAIR_ROOT": str(workspace),
        },
    }


def render_cursor_mcp_config(workspace: Path) -> dict[str, object]:
    python_bin = detect_python_bin(workspace)
    return {
        "mcpServers": {
            "ai-pair-memory": {
                "command": str(python_bin),
                "args": [
                    str(workspace / "tools" / "shared_memory_mcp" / "serve.py"),
                ],
                "env": {
                    "AI_PAIR_ROOT": str(workspace),
                },
            }
        }
    }


def refresh_ai_context(workspace: Path) -> None:
    path = workspace / "AI_CONTEXT.md"
    content = path.read_text(encoding="utf-8")
    now = utc_now()
    content = content.replace("REPLACE_WITH_PROJECT_ROOT", str(workspace))
    content = content.replace("- Last updated: 2026-05-17 00:00:00 +00:00", f"- Last updated: {now}")
    content = content.replace("- Context created: 2026-05-17 00:00:00 +00:00", f"- Context created: {now}")
    path.write_text(content, encoding="utf-8")


def ensure_coldstart_handoff(workspace: Path) -> Path:
    existing = newest_handoff_path(workspace)
    if existing is not None:
        return existing

    now = utc_now()
    path = workspace / handoff_filename_for_today()
    body = "\n".join(
        [
            "# Project Cold-Start Handoff",
            "",
            "## Context Metadata",
            "",
            f"- Context created: {now}",
            f"- Last updated: {now}",
            "- Timezone: UTC",
            f"- Workspace root: `{workspace}`",
            "",
            "## Project Background",
            "",
            f"- Project name: `{workspace.name}`",
            "- Domain: shared memory workflow for Cursor's built-in Claude and the Kimi extension",
            f"- Repo or workspace locations: `{workspace}`",
            "- High-level goal: keep planning, execution, review, and fix context reusable across new chats without copying private transcripts",
            "",
            "## Compressed Conversation History",
            "",
            "- Original user request: bootstrap the shared-memory workflow template",
            "- Major request changes: align the strong-model role with Cursor's built-in Claude, require more detailed plans, and keep the workflow synchronized with the local context-coldstart-pack skill",
            "- Decision sequence: initialize shared-memory MCP, split planning/review from execution/fix, require detailed strong-model planning, then keep durable state in Markdown files plus `.ai-pair/`",
            "- Important turning points: medium and large changes must pass through OpenSpec before Kimi executes",
            "",
            "## Persistent Context",
            "",
            "- Stable terminology: Claude owns planning/review, Kimi owns execution/fix",
            "- Durable rules: `.ai-pair/` is the active change source of truth; `AI_CONTEXT.md` is compact memory; this handoff is the detailed restart pack",
            "- Metrics or formulas: `high` and `critical` findings block `done`; `design_drift` routes back to `planning`",
            "- Environment constraints: shared-memory MCP is optional but preferred",
            "- Key files and modules: `AGENTS.md`, `AI_CONTEXT.md`, `.ai-pair/`, `.cursor/rules/`, `tools/shared_memory_mcp/`, `spec/`",
            "- Workflow and code-style constraints: read both durable memory files before substantive work, keep them synchronized after meaningful rounds, and write plans detailed enough that Claude could execute them directly",
            "",
            "## Current State",
            "",
            "- Current objective: initialize the workflow for a real project",
            "- Current status: Bootstrap only",
            "- Latest blockers: None recorded",
            "- Latest next step: connect Claude and Kimi to the shared-memory workflow, then start the first planned change",
            "- Latest important artifacts: `AI_CONTEXT.md`, this handoff file, `.ai-pair/`, and `.cursor/mcp.json`",
            "",
            "## Experiments Snapshot",
            "",
            "- Current or latest experiment: Not run in this session",
            "- Commands: None",
            "- Hyperparameters: None",
            "- Checkpoints: None",
            "- Results: None",
            "",
            "## Key Files And Modules",
            "",
            "- Documents: `README.md`, `AGENTS.md`, `AI_CONTEXT.md`",
            "- Scripts: `scripts/bootstrap_project.py`, `tools/shared_memory_mcp/serve.py`",
            "- Entry points: `.cursor/rules/`, `.cursor/mcp.json`, Kimi MCP setup",
            "- Results and artifacts: `.ai-pair/status.json`, `.ai-pair/current_handoff.md`, `.ai-pair/review_findings.md`",
            "",
            "## Completed Work",
            "",
            "- Shared-memory template scaffolded",
            "- Claude/Kimi ownership model defined",
            "- Bootstrap flow documented",
            "",
            "## Current Blockers And Risks",
            "",
            "- No blocker recorded",
            "- Risk: if durable memory files drift from `.ai-pair/`, a fresh session may start from stale assumptions",
            "",
            "## Workflow, Tone, And Style Constraints",
            "",
            "- Tone: direct, operational, and audit-friendly",
            "- Explanation style: concise summaries with exact file paths",
            "- Workflow order: Claude plan/review -> Kimi execute/fix -> Claude final review",
            "- Coding constraints: shared-memory writes should prefer MCP when available",
            "- Documentation style: keep durable memory high-signal and avoid raw transcript dumps",
            "",
            "## Next-Step Recovery Instructions",
            "",
            "- First files to read: `AGENTS.md`, `AI_CONTEXT.md`, the newest `COLDSTART_HANDOFF_*.md`, `.ai-pair/status.json`, `.ai-pair/current_handoff.md`",
            "- Exact next step: decide whether the next requested change needs OpenSpec before handing work to Kimi",
            "- Recommended first prompt for a new session: `Read AGENTS.md, AI_CONTEXT.md, the newest COLDSTART_HANDOFF_*.md, and .ai-pair/current_handoff.md, then continue the current change.`",
            "",
            "## Round Log",
            "",
            f"### {now}",
            "",
            "- User request: Bootstrapped the workflow template",
            "- Decisions or changes: Initialized durable memory files plus shared `.ai-pair/` state",
            "- Files touched: `AI_CONTEXT.md`, this handoff file, `.ai-pair/`, `.cursor/mcp.json`",
            "- Experiment updates: None",
            "- New blockers or open questions: Keep the durable memory files synchronized with `.ai-pair/`",
            "",
        ]
    )
    path.write_text(body, encoding="utf-8")
    return path


def refresh_status(workspace: Path) -> None:
    path = workspace / ".ai-pair" / "status.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["summary"] = "Bootstrap complete. Cursor's built-in Claude should now write a detailed plan for the first change or trigger the OpenSpec gate."
    payload["updated_at"] = utc_now()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def refresh_handoff(workspace: Path) -> None:
    path = workspace / ".ai-pair" / "current_handoff.md"
    body = "\n".join(
        [
            "# Current Handoff",
            "",
            "## Owner",
            "",
            "- Current owner: `claude_plan`",
            "- Current phase: `planning`",
            "",
            "## Required Action",
            "",
            "Cursor's built-in Claude should inspect the requested change, decide whether the OpenSpec gate applies, and then hand execution to Kimi.",
            "",
            "The plan should be detailed enough that Claude could execute it directly if the strong model kept the implementation role.",
            "",
            "Kimi should wait until ownership moves to `kimi_execute`.",
            "",
        ]
    )
    path.write_text(body, encoding="utf-8")


def detect_python_bin(workspace: Path) -> str | Path:
    windows_python = workspace / ".venv" / "Scripts" / "python.exe"
    posix_python = workspace / ".venv" / "bin" / "python"
    if windows_python.exists():
        return windows_python
    if posix_python.exists():
        return posix_python
    return "python"


def refresh_cursor_mcp_config(workspace: Path) -> None:
    path = workspace / ".cursor" / "mcp.json"
    payload = render_cursor_mcp_config(workspace)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def maybe_create_venv(workspace: Path, install_dev: bool) -> None:
    venv_dir = workspace / ".venv"
    if not venv_dir.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, cwd=workspace)
    python_bin = venv_dir / ("Scripts/python.exe" if sys.platform.startswith("win") else "bin/python")
    extras = ".[dev]" if install_dev else "."
    subprocess.run([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"], check=True, cwd=workspace)
    subprocess.run([str(python_bin), "-m", "pip", "install", "-e", extras], check=True, cwd=workspace)


def bootstrap_workspace(workspace: Path, create_venv: bool, install_dev: bool) -> None:
    if create_venv:
        maybe_create_venv(workspace, install_dev=install_dev)
    refresh_ai_context(workspace)
    ensure_coldstart_handoff(workspace)
    refresh_status(workspace)
    refresh_handoff(workspace)
    refresh_cursor_mcp_config(workspace)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap the ai-pair-memory-template workspace.")
    parser.add_argument("--workspace", type=Path, default=Path("."), help="Path to the template workspace root.")
    parser.add_argument("--skip-venv", action="store_true", help="Skip creating .venv and installing package dependencies.")
    parser.add_argument("--install-dev", action="store_true", help="Install dev dependencies when creating the venv.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    workspace = args.workspace.resolve()
    bootstrap_workspace(workspace, create_venv=not args.skip_venv, install_dev=args.install_dev)
    print("Bootstrapped ai-pair-memory-template at", workspace)
    print("Suggested Kimi MCP config:")
    print(json.dumps(render_kimi_stdio_config(workspace), indent=2))


if __name__ == "__main__":
    main()
