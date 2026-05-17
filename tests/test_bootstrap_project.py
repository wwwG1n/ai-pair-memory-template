from __future__ import annotations

import json
from pathlib import Path

from scripts.bootstrap_project import (
    bootstrap_workspace,
    detect_python_bin,
    render_cursor_mcp_config,
    render_kimi_stdio_config,
    should_use_openspec,
)


def create_workspace(tmp_path: Path) -> Path:
    (tmp_path / ".ai-pair").mkdir(parents=True, exist_ok=True)
    (tmp_path / "AI_CONTEXT.md").write_text(
        "# AI Context Journal\n\n"
        "- Context created: 2026-05-17 00:00:00 +00:00\n"
        "- Last updated: 2026-05-17 00:00:00 +00:00\n"
        "- Workspace root: `REPLACE_WITH_PROJECT_ROOT`\n",
        encoding="utf-8",
    )
    (tmp_path / ".ai-pair" / "status.json").write_text(
        json.dumps(
            {
                "phase": "planning",
                "owner": "cursor_plan",
                "change_id": None,
                "summary": "Bootstrap state.",
                "updated_at": "2026-05-17T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / ".ai-pair" / "current_handoff.md").write_text("# Current Handoff\n", encoding="utf-8")
    return tmp_path


def test_should_use_openspec_flags_medium_and_large_changes() -> None:
    assert should_use_openspec(
        new_feature=False,
        touches_api_or_schema=False,
        production_files_touched=4,
        estimated_minutes=20,
    )
    assert should_use_openspec(
        new_feature=False,
        touches_api_or_schema=True,
        production_files_touched=1,
        estimated_minutes=20,
    )
    assert not should_use_openspec(
        new_feature=False,
        touches_api_or_schema=False,
        production_files_touched=2,
        estimated_minutes=30,
    )


def test_render_kimi_stdio_config_points_to_server(tmp_path: Path) -> None:
    cfg = render_kimi_stdio_config(tmp_path)
    assert cfg["command"] == "python"
    assert str(tmp_path / "tools" / "shared_memory_mcp" / "serve.py") in cfg["args"][0]
    assert cfg["env"]["AI_PAIR_ROOT"] == str(tmp_path)


def test_bootstrap_workspace_rewrites_placeholders(tmp_path: Path) -> None:
    workspace = create_workspace(tmp_path)
    (workspace / ".cursor").mkdir(parents=True, exist_ok=True)
    (workspace / ".cursor" / "mcp.json").write_text("{}", encoding="utf-8")

    bootstrap_workspace(workspace, create_venv=False, install_dev=False)

    ai_context = (workspace / "AI_CONTEXT.md").read_text(encoding="utf-8")
    status = json.loads((workspace / ".ai-pair" / "status.json").read_text(encoding="utf-8"))
    handoff = (workspace / ".ai-pair" / "current_handoff.md").read_text(encoding="utf-8")
    cursor_mcp = json.loads((workspace / ".cursor" / "mcp.json").read_text(encoding="utf-8"))

    assert "REPLACE_WITH_PROJECT_ROOT" not in ai_context
    assert str(workspace) in ai_context
    assert "Bootstrap complete." in status["summary"]
    assert "Cursor should inspect the requested change" in handoff
    assert cursor_mcp["mcpServers"]["ai-pair-memory"]["command"] == "python"


def test_detect_python_bin_prefers_workspace_venv(tmp_path: Path) -> None:
    python_bin = tmp_path / ".venv" / "Scripts" / "python.exe"
    python_bin.parent.mkdir(parents=True, exist_ok=True)
    python_bin.write_text("", encoding="utf-8")

    assert detect_python_bin(tmp_path) == python_bin


def test_render_cursor_mcp_config_uses_detected_python(tmp_path: Path) -> None:
    python_bin = tmp_path / ".venv" / "Scripts" / "python.exe"
    python_bin.parent.mkdir(parents=True, exist_ok=True)
    python_bin.write_text("", encoding="utf-8")

    cfg = render_cursor_mcp_config(tmp_path)

    assert cfg["mcpServers"]["ai-pair-memory"]["command"] == str(python_bin)
