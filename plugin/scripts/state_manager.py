"""state.json 读写与状态机。

每个视频项目一个 .video/state.json，记录当前阶段、配置、时间戳。
phase 顺序：init → write → review → visual → done
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VIDEO_PHASES = ["init", "write", "review", "visual", "done"]


class InvalidTransition(Exception):
    """非法的 phase 转移。"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateManager:
    def __init__(self, project_root: str | Path):
        self.root = Path(project_root).resolve()
        self.state_file = self.root / ".video" / "state.json"

    def _read_raw(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {}
        return json.loads(self.state_file.read_text(encoding="utf-8"))

    def _write_raw(self, data: dict[str, Any]) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def init(self, video_id: str, config: dict[str, Any]) -> None:
        """初始化新项目。"""
        data = {
            "video_id": video_id,
            "phase": "init",
            "phases_completed": ["init"],
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "config": config,
        }
        self._write_raw(data)

    def read(self) -> dict[str, Any]:
        """读取 state.json。"""
        return self._read_raw()

    def current_phase(self) -> str:
        """返回当前 phase。"""
        return self._read_raw().get("phase", "init")

    def set_phase(self, new_phase: str) -> None:
        """设置新 phase。校验转移合法性。"""
        if new_phase not in VIDEO_PHASES:
            raise ValueError(f"Unknown phase: {new_phase}")

        data = self._read_raw()
        current = data.get("phase", "init")

        # 已 done 之后允许任意转移（重跑）
        if current == "done":
            data["phase"] = new_phase
            data["updated_at"] = _now_iso()
            data["re_run"] = True
            self._write_raw(data)
            return

        # 不允许回退
        if VIDEO_PHASES.index(new_phase) < VIDEO_PHASES.index(current):
            raise InvalidTransition(
                f"Cannot go backward: {current} → {new_phase}"
            )

        # 不允许跳过（done 除外）
        if VIDEO_PHASES.index(new_phase) > VIDEO_PHASES.index(current) + 1:
            raise InvalidTransition(
                f"Cannot skip phase: {current} → {new_phase}. "
                f"Must go through {VIDEO_PHASES[VIDEO_PHASES.index(current) + 1]}."
            )

        data["phase"] = new_phase
        if new_phase not in data.get("phases_completed", []):
            data.setdefault("phases_completed", []).append(new_phase)
        data["updated_at"] = _now_iso()
        self._write_raw(data)
