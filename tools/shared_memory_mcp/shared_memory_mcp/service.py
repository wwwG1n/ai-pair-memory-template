from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import EventRecord, PHASES, SEVERITIES, ReviewFinding, WorkflowStatus, utc_now_iso
from .store import SharedMemoryStore


class SharedMemoryService:
    def __init__(self, store: SharedMemoryStore) -> None:
        self.store = store
        self.store.ensure_layout()

    def get_context_resource(self) -> str:
        status = self.store.read_status()
        return "\n".join(
            [
                "# Shared Context Snapshot",
                "",
                f"- Phase: `{status.phase}`",
                f"- Owner: `{status.owner}`",
                f"- Change ID: `{status.change_id or 'none'}`",
                f"- Summary: {status.summary}",
                "",
                "## Current Handoff",
                "",
                self.store.read_current_handoff().strip(),
                "",
                "## Current Blockers",
                "",
                self.store.read_blockers().strip(),
            ]
        ).strip() + "\n"

    def get_tasks_resource(self) -> str:
        return self.store.read_task_board()

    def get_handoff_resource(self) -> str:
        return self.store.read_current_handoff()

    def get_review_resource(self) -> str:
        return self.store.read_review_findings()

    def append_event(
        self,
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
        self._validate_phase(phase)
        self._validate_severity(severity)
        event = EventRecord(
            ts=utc_now_iso(),
            agent=agent,
            phase=phase,
            kind=kind,
            change_id=change_id,
            task_id=task_id,
            status=status,
            severity=severity,
            summary=summary,
            artifacts=artifacts or [],
        )
        self.store.append_event(event)
        return event.to_dict()

    def update_status(
        self,
        phase: str,
        owner: str,
        summary: str,
        change_id: str | None = None,
        event_agent: str = "shared-memory-mcp",
        event_kind: str = "status_update",
    ) -> dict[str, object]:
        self._validate_phase(phase)
        status = WorkflowStatus(
            phase=phase,  # type: ignore[arg-type]
            owner=owner,
            change_id=change_id,
            summary=summary,
            updated_at=utc_now_iso(),
        )
        self.store.write_status(status)
        event = self.append_event(
            agent=event_agent,
            phase=phase,
            kind=event_kind,
            change_id=change_id,
            summary=summary,
            status="ok",
            severity="info",
            artifacts=[".ai-pair/status.json"],
        )
        return {"status": status.to_dict(), "event": event}

    def render_handoff(
        self,
        target_agent: str,
        focus: str,
        notes: str = "",
        change_id: str | None = None,
        task_ids: list[str] | None = None,
    ) -> dict[str, object]:
        status = self.store.read_status()
        task_list = task_ids or []
        findings_excerpt = self._open_findings_as_lines()
        lines = [
            "# Current Handoff",
            "",
            "## Owner",
            "",
            f"- Current owner: `{target_agent}`",
            f"- Current phase: `{status.phase}`",
            f"- Change ID: `{change_id or status.change_id or 'none'}`",
            "",
            "## Focus",
            "",
            focus,
        ]
        if task_list:
            lines.extend(["", "## Target Tasks", ""])
            lines.extend([f"- `{task_id}`" for task_id in task_list])
        if notes:
            lines.extend(["", "## Notes", "", notes])
        if findings_excerpt:
            lines.extend(["", "## Open Findings Snapshot", ""])
            lines.extend(findings_excerpt)
        body = "\n".join(lines).strip() + "\n"
        self.store.write_current_handoff(body)
        event = self.append_event(
            agent="shared-memory-mcp",
            phase=status.phase,
            kind="handoff_rendered",
            change_id=change_id or status.change_id,
            summary=f"Rendered handoff for {target_agent}: {focus}",
            artifacts=[".ai-pair/current_handoff.md"],
        )
        return {"target_agent": target_agent, "handoff_path": str(self.store.current_handoff_path), "event": event}

    def record_review(
        self,
        reviewer: str,
        findings: list[dict[str, Any]],
        summary: str,
        change_id: str | None = None,
    ) -> dict[str, object]:
        normalized = [self._normalize_finding(item) for item in findings]
        markdown = self._render_review_markdown(reviewer, summary, normalized)
        self.store.write_review_findings(markdown)
        next_phase, next_owner = self._next_phase_from_findings(normalized)
        self.update_status(
            phase=next_phase,
            owner=next_owner,
            summary=summary,
            change_id=change_id,
            event_agent=reviewer,
            event_kind="review_status",
        )
        for finding in normalized:
            self.append_event(
                agent=reviewer,
                phase=next_phase,
                kind=f"review_finding:{finding.kind}",
                change_id=change_id,
                task_id=finding.task_id,
                status=finding.status,
                severity=finding.severity,
                summary=f"{finding.id} {finding.title}",
                artifacts=finding.file_refs,
            )

        if next_phase == "planning":
            focus = "Replan the change. Review found design drift that should not be patched locally."
            handoff_owner = "codex_plan"
        elif next_phase == "fix_pending":
            focus = "Fix the open review findings before asking Codex for another review pass."
            handoff_owner = "kimi_fix"
        else:
            focus = "No open findings remain. Confirm final status and archive the change if appropriate."
            handoff_owner = "codex_review"

        handoff = self.render_handoff(
            target_agent=handoff_owner,
            focus=focus,
            notes=summary,
            change_id=change_id,
            task_ids=[finding.task_id for finding in normalized if finding.task_id],
        )
        return {
            "next_phase": next_phase,
            "next_owner": handoff_owner,
            "review_path": str(self.store.review_findings_path),
            "handoff": handoff,
            "findings": [asdict(finding) for finding in normalized],
        }

    def search_events(
        self,
        query: str = "",
        agent: str | None = None,
        phase: str | None = None,
        change_id: str | None = None,
        task_id: str | None = None,
        severity: str | None = None,
        kind: str | None = None,
        limit: int = 20,
    ) -> dict[str, object]:
        lowered_query = query.lower().strip()
        events = []
        for event in self.store.iter_events():
            if agent and event.agent != agent:
                continue
            if phase and event.phase != phase:
                continue
            if change_id and event.change_id != change_id:
                continue
            if task_id and event.task_id != task_id:
                continue
            if severity and event.severity != severity:
                continue
            if kind and event.kind != kind:
                continue
            if lowered_query and lowered_query not in event.summary.lower():
                continue
            events.append(event.to_dict())
            if len(events) >= limit:
                break
        return {"count": len(events), "events": events}

    def _normalize_finding(self, raw: dict[str, Any]) -> ReviewFinding:
        severity = str(raw.get("severity", "medium"))
        self._validate_severity(severity)
        return ReviewFinding(
            id=str(raw.get("id") or f"finding-{utc_now_iso()}"),
            severity=severity,
            title=str(raw.get("title") or "Untitled finding"),
            summary=str(raw.get("summary") or ""),
            status=str(raw.get("status") or "open"),
            kind=str(raw.get("kind") or "defect"),
            task_id=str(raw["task_id"]) if raw.get("task_id") else None,
            file_refs=[str(item) for item in raw.get("file_refs", [])],
            suggested_action=str(raw["suggested_action"]) if raw.get("suggested_action") else None,
        )

    def _render_review_markdown(self, reviewer: str, summary: str, findings: list[ReviewFinding]) -> str:
        lines = [
            "# Review Findings",
            "",
            f"- Reviewer: `{reviewer}`",
            f"- Summary: {summary}",
            "",
        ]
        if not findings:
            lines.extend(["No review findings recorded.", ""])
            return "\n".join(lines)

        open_findings = [item for item in findings if item.status != "closed"]
        lines.extend(
            [
                f"- Total findings: {len(findings)}",
                f"- Open findings: {len(open_findings)}",
                "",
                "## Findings",
                "",
            ]
        )
        for finding in findings:
            lines.append(finding.to_markdown())
        return "\n".join(lines).rstrip() + "\n"

    def _next_phase_from_findings(self, findings: list[ReviewFinding]) -> tuple[str, str]:
        open_findings = [item for item in findings if item.status != "closed"]
        if any(item.kind == "design_drift" for item in open_findings):
            return "planning", "codex_plan"
        if open_findings:
            return "fix_pending", "kimi_fix"
        return "done", "codex_review"

    def _open_findings_as_lines(self) -> list[str]:
        content = self.store.read_review_findings().strip()
        if not content or content == "# Review Findings\n\nNo review findings recorded yet.":
            return []
        return [f"- {line}" for line in content.splitlines()[:8] if line.strip()]

    def _validate_phase(self, phase: str) -> None:
        if phase not in PHASES:
            raise ValueError(f"Unsupported phase: {phase}")

    def _validate_severity(self, severity: str) -> None:
        if severity not in SEVERITIES:
            raise ValueError(f"Unsupported severity: {severity}")
