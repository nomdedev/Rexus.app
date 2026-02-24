"""
Bridge de eventos para Pixel Agents.

Pixel Agents observa archivos JSONL en ~/.claude/projects/<workspace>. Este
bridge escribe eventos con formato compatible para que los agentes internos de
Rexus puedan reflejar actividad en el panel de Pixel Agents.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
import json
import os
import threading
import uuid


def _workspace_slug(workspace: str) -> str:
    return workspace.replace(":", "-").replace("\\", "-").replace("/", "-")


def _tool_name_from_task(task_type: str) -> str:
    mapping = {
        "audit": "Task",
        "analyze": "Read",
        "report": "Write",
        "execute": "Bash",
    }
    return mapping.get((task_type or "").lower(), "Task")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PixelTaskRef:
    session_file: Path
    tool_id: str
    task_type: str


class PixelAgentsBridge:
    def __init__(self, workspace_root: Optional[Path] = None):
        root = workspace_root or Path.cwd()
        self.workspace_root = root
        self.project_dir = Path.home() / ".claude" / "projects" / _workspace_slug(str(root))
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._agent_session_file: Dict[str, Path] = {}

    def _discover_session_files(self):
        return sorted(self.project_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)

    def _get_or_create_session_file(self, agent_id: str) -> Path:
        if agent_id in self._agent_session_file:
            return self._agent_session_file[agent_id]

        existing = self._discover_session_files()
        if existing:
            idx = len(self._agent_session_file) % len(existing)
            target = existing[idx]
        else:
            target = self.project_dir / f"{uuid.uuid4()}.jsonl"
            target.touch(exist_ok=True)

        self._agent_session_file[agent_id] = target
        return target

    def _append_line(self, file_path: Path, payload: dict) -> None:
        line = json.dumps(payload, ensure_ascii=False)
        with open(file_path, "a", encoding="utf-8") as handle:
            handle.write(line + os.linesep)

    def start_task(self, agent_id: str, description: str, task_type: str) -> PixelTaskRef:
        with self._lock:
            session_file = self._get_or_create_session_file(agent_id)
            tool_id = f"tool_{uuid.uuid4().hex[:12]}"
            tool_name = _tool_name_from_task(task_type)

            self._append_line(
                session_file,
                {
                    "type": "assistant",
                    "timestamp": _now_iso(),
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": tool_id,
                                "name": tool_name,
                                "input": {
                                    "description": description,
                                },
                            }
                        ]
                    },
                },
            )

            return PixelTaskRef(session_file=session_file, tool_id=tool_id, task_type=task_type)

    def update_progress(self, task_ref: PixelTaskRef, description: str, progress: int) -> None:
        with self._lock:
            self._append_line(
                task_ref.session_file,
                {
                    "type": "progress",
                    "timestamp": _now_iso(),
                    "parentToolUseID": task_ref.tool_id,
                    "data": {
                        "type": "mcp_progress",
                        "message": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"{description} ({progress}%)",
                                }
                            ]
                        },
                    },
                },
            )

    def complete_task(self, task_ref: PixelTaskRef, result: str, is_error: bool = False) -> None:
        with self._lock:
            self._append_line(
                task_ref.session_file,
                {
                    "type": "user",
                    "timestamp": _now_iso(),
                    "message": {
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": task_ref.tool_id,
                                "content": result,
                                "is_error": is_error,
                            }
                        ]
                    },
                },
            )
            self._append_line(
                task_ref.session_file,
                {
                    "type": "system",
                    "subtype": "turn_duration",
                    "timestamp": _now_iso(),
                },
            )


_bridge_singleton: Optional[PixelAgentsBridge] = None


def get_pixel_bridge() -> PixelAgentsBridge:
    global _bridge_singleton
    if _bridge_singleton is None:
        _bridge_singleton = PixelAgentsBridge()
    return _bridge_singleton
