from __future__ import annotations

import json
import threading
from pathlib import Path

from .models import EventRecord, WorkflowStatus


class SharedMemoryStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.ai_pair_dir = self.root / ".ai-pair"
        self.ai_context_path = self.root / "AI_CONTEXT.md"
        self.status_path = self.ai_pair_dir / "status.json"
        self.events_path = self.ai_pair_dir / "events.jsonl"
        self.task_board_path = self.ai_pair_dir / "task_board.md"
        self.current_handoff_path = self.ai_pair_dir / "current_handoff.md"
        self.review_findings_path = self.ai_pair_dir / "review_findings.md"
        self.blockers_path = self.ai_pair_dir / "blockers.md"
        self._lock = threading.Lock()

    def ensure_layout(self) -> None:
        self.ai_pair_dir.mkdir(parents=True, exist_ok=True)
        defaults: dict[Path, str] = {
            self.ai_context_path: "# AI Context Journal\n",
            self.task_board_path: "# Task Board\n",
            self.current_handoff_path: "# Current Handoff\n",
            self.review_findings_path: "# Review Findings\n",
            self.blockers_path: "# Blockers\n",
            self.events_path: "",
        }
        for path, content in defaults.items():
            if not path.exists():
                path.write_text(content, encoding="utf-8")

    def _read_text(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def _write_text(self, path: Path, content: str) -> None:
        with self._lock:
            path.write_text(content, encoding="utf-8")

    def read_status(self) -> WorkflowStatus:
        payload = json.loads(self.status_path.read_text(encoding="utf-8"))
        return WorkflowStatus(**payload)

    def write_status(self, status: WorkflowStatus) -> None:
        with self._lock:
            self.status_path.write_text(
                json.dumps(status.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    def append_event(self, event: EventRecord) -> None:
        with self._lock:
            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    def iter_events(self) -> list[EventRecord]:
        if not self.events_path.exists():
            return []
        events: list[EventRecord] = []
        for raw_line in self.events_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            events.append(EventRecord(**json.loads(line)))
        return events

    def read_ai_context(self) -> str:
        return self._read_text(self.ai_context_path)

    def read_task_board(self) -> str:
        return self._read_text(self.task_board_path)

    def read_current_handoff(self) -> str:
        return self._read_text(self.current_handoff_path)

    def write_current_handoff(self, content: str) -> None:
        self._write_text(self.current_handoff_path, content)

    def read_review_findings(self) -> str:
        return self._read_text(self.review_findings_path)

    def write_review_findings(self, content: str) -> None:
        self._write_text(self.review_findings_path, content)

    def read_blockers(self) -> str:
        return self._read_text(self.blockers_path)
