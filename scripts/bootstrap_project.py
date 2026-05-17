from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def refresh_status(workspace: Path) -> None:
    path = workspace / ".ai-pair" / "status.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["summary"] = "Bootstrap complete. Cursor should now plan the first change or trigger the OpenSpec gate."
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
            "- Current owner: `cursor_plan`",
            "- Current phase: `planning`",
            "",
            "## Required Action",
            "",
            "Cursor should inspect the requested change, decide whether the OpenSpec gate applies, and then hand execution to Kimi.",
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
