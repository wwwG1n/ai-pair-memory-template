from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .service import SharedMemoryService
from .store import SharedMemoryStore


def build_server(root: str | Path | None = None) -> FastMCP:
    workspace_root = Path(root or os.environ.get("AI_PAIR_ROOT") or Path.cwd()).resolve()
    service = SharedMemoryService(SharedMemoryStore(workspace_root))
    mcp = FastMCP("AI Pair Memory", json_response=True)

    @mcp.resource("context://current")
    def context_current() -> str:
        return service.get_context_resource()

    @mcp.resource("tasks://open")
    def tasks_open() -> str:
        return service.get_tasks_resource()

    @mcp.resource("handoff://latest")
    def handoff_latest() -> str:
        return service.get_handoff_resource()

    @mcp.resource("review://open-findings")
    def review_open_findings() -> str:
        return service.get_review_resource()

    @mcp.tool()
    def append_event(
        agent: str,
        phase: str,
        kind: str,
        summary: str,
        change_id: str | None = None,
        task_id: str | None = None,
        status: str = "ok",
        severity: str = "info",
        artifacts: list[str] | None = None,
    ) -> dict[str, object]:
        return service.append_event(
            agent=agent,
            phase=phase,
            kind=kind,
            summary=summary,
            change_id=change_id,
            task_id=task_id,
            status=status,
            severity=severity,
            artifacts=artifacts,
        )

    @mcp.tool()
    def update_status(
        phase: str,
        owner: str,
        summary: str,
        change_id: str | None = None,
        event_agent: str = "shared-memory-mcp",
        event_kind: str = "status_update",
    ) -> dict[str, object]:
        return service.update_status(
            phase=phase,
            owner=owner,
            summary=summary,
            change_id=change_id,
            event_agent=event_agent,
            event_kind=event_kind,
        )

    @mcp.tool()
    def render_handoff(
        target_agent: str,
        focus: str,
        notes: str = "",
        change_id: str | None = None,
        task_ids: list[str] | None = None,
    ) -> dict[str, object]:
        return service.render_handoff(
            target_agent=target_agent,
            focus=focus,
            notes=notes,
            change_id=change_id,
            task_ids=task_ids,
        )

    @mcp.tool()
    def record_review(
        reviewer: str,
        findings: list[dict[str, Any]],
        summary: str,
        change_id: str | None = None,
    ) -> dict[str, object]:
        return service.record_review(
            reviewer=reviewer,
            findings=findings,
            summary=summary,
            change_id=change_id,
        )

    @mcp.tool()
    def search_events(
        query: str = "",
        agent: str | None = None,
        phase: str | None = None,
        change_id: str | None = None,
        task_id: str | None = None,
        severity: str | None = None,
        kind: str | None = None,
        limit: int = 20,
    ) -> dict[str, object]:
        return service.search_events(
            query=query,
            agent=agent,
            phase=phase,
            change_id=change_id,
            task_id=task_id,
            severity=severity,
            kind=kind,
            limit=limit,
        )

    return mcp


def main() -> None:
    build_server().run(transport="stdio")
