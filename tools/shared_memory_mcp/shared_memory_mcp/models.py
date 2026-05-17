from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal


Phase = Literal["planning", "approved", "executing", "review_pending", "fix_pending", "done"]
Severity = Literal["info", "low", "medium", "high", "critical"]

PHASES: set[str] = {"planning", "approved", "executing", "review_pending", "fix_pending", "done"}
SEVERITIES: set[str] = {"info", "low", "medium", "high", "critical"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class WorkflowStatus:
    phase: Phase
    owner: str
    change_id: str | None
    summary: str
    updated_at: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class EventRecord:
    ts: str
    agent: str
    phase: str
    kind: str
    change_id: str | None
    task_id: str | None
    status: str
    severity: str
    summary: str
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ReviewFinding:
    id: str
    severity: str
    title: str
    summary: str
    status: str = "open"
    kind: str = "defect"
    task_id: str | None = None
    file_refs: list[str] = field(default_factory=list)
    suggested_action: str | None = None

    def to_markdown(self) -> str:
        lines = [
            f"### {self.id}: {self.title}",
            "",
            f"- Severity: `{self.severity}`",
            f"- Status: `{self.status}`",
            f"- Kind: `{self.kind}`",
        ]
        if self.task_id:
            lines.append(f"- Task ID: `{self.task_id}`")
        if self.file_refs:
            lines.append(f"- File refs: {', '.join(self.file_refs)}")
        if self.suggested_action:
            lines.append(f"- Suggested action: {self.suggested_action}")
        lines.extend(["", self.summary, ""])
        return "\n".join(lines)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
