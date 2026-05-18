from __future__ import annotations

import json
from pathlib import Path

from shared_memory_mcp.service import SharedMemoryService
from shared_memory_mcp.store import SharedMemoryStore


def seed_workspace(root: Path) -> SharedMemoryService:
    ai_pair = root / ".ai-pair"
    ai_pair.mkdir(parents=True, exist_ok=True)
    (root / "AI_CONTEXT.md").write_text("# AI Context Journal\n", encoding="utf-8")
    (ai_pair / "status.json").write_text(
        json.dumps(
            {
                "phase": "review_pending",
                "owner": "codex_review",
                "change_id": "add-shared-memory",
                "summary": "Ready for review.",
                "updated_at": "2026-05-17T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (ai_pair / "events.jsonl").write_text("", encoding="utf-8")
    (ai_pair / "task_board.md").write_text("# Task Board\n\n- [ ] task-1\n", encoding="utf-8")
    (ai_pair / "current_handoff.md").write_text("# Current Handoff\n\nInitial handoff.\n", encoding="utf-8")
    (ai_pair / "review_findings.md").write_text("# Review Findings\n\nNo review findings recorded yet.\n", encoding="utf-8")
    (ai_pair / "blockers.md").write_text("# Blockers\n\nNone.\n", encoding="utf-8")
    return SharedMemoryService(SharedMemoryStore(root))


def test_append_event_persists_jsonl(tmp_path: Path) -> None:
    service = seed_workspace(tmp_path)

    event = service.append_event(
        agent="cursor",
        phase="planning",
        kind="plan_created",
        summary="Created a plan.",
        severity="info",
        artifacts=["plan.md"],
    )

    assert event["agent"] == "cursor"
    lines = (tmp_path / ".ai-pair" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["kind"] == "plan_created"
    assert payload["artifacts"] == ["plan.md"]


def test_update_status_rewrites_status_file(tmp_path: Path) -> None:
    service = seed_workspace(tmp_path)

    result = service.update_status(
        phase="executing",
        owner="kimi_execute",
        summary="Execution started.",
        change_id="add-shared-memory",
    )

    status_payload = json.loads((tmp_path / ".ai-pair" / "status.json").read_text(encoding="utf-8"))
    assert status_payload["phase"] == "executing"
    assert status_payload["owner"] == "kimi_execute"
    assert result["status"]["change_id"] == "add-shared-memory"


def test_record_review_routes_fix_pending_for_open_findings(tmp_path: Path) -> None:
    service = seed_workspace(tmp_path)

    result = service.record_review(
        reviewer="codex_review",
        summary="Found a regression and missing test.",
        findings=[
            {
                "id": "RV-001",
                "severity": "high",
                "title": "Regression on retry path",
                "summary": "The retry path now skips validation.",
                "task_id": "task-2",
                "file_refs": ["backend/service.py:42"],
            }
        ],
        change_id="add-shared-memory",
    )

    status_payload = json.loads((tmp_path / ".ai-pair" / "status.json").read_text(encoding="utf-8"))
    handoff = (tmp_path / ".ai-pair" / "current_handoff.md").read_text(encoding="utf-8")
    findings = (tmp_path / ".ai-pair" / "review_findings.md").read_text(encoding="utf-8")

    assert result["next_phase"] == "fix_pending"
    assert status_payload["phase"] == "fix_pending"
    assert "kimi_fix" in handoff
    assert "RV-001" in findings


def test_record_review_routes_planning_for_design_drift(tmp_path: Path) -> None:
    service = seed_workspace(tmp_path)

    result = service.record_review(
        reviewer="codex_review",
        summary="Execution drifted away from the approved design.",
        findings=[
            {
                "id": "RV-010",
                "severity": "medium",
                "title": "Design drift",
                "summary": "The implementation no longer follows the approved data flow.",
                "kind": "design_drift",
            }
        ],
        change_id="add-shared-memory",
    )

    status_payload = json.loads((tmp_path / ".ai-pair" / "status.json").read_text(encoding="utf-8"))
    assert result["next_phase"] == "planning"
    assert status_payload["phase"] == "planning"
    assert status_payload["owner"] == "codex_plan"


def test_search_events_filters_by_query_and_severity(tmp_path: Path) -> None:
    service = seed_workspace(tmp_path)
    service.append_event(
        agent="cursor",
        phase="planning",
        kind="plan_created",
        summary="Create shared memory plan.",
        severity="info",
    )
    service.append_event(
        agent="codex_review",
        phase="fix_pending",
        kind="review_finding:defect",
        summary="Critical auth regression.",
        severity="critical",
    )

    result = service.search_events(query="auth", severity="critical")

    assert result["count"] == 1
    assert result["events"][0]["summary"] == "Critical auth regression."
