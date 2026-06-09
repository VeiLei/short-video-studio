"""测试 state.json 的读写与状态机转移。"""
import json
import sys
from pathlib import Path

import pytest

# 把 plugin/scripts 加入 path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from state_manager import StateManager, InvalidTransition, VIDEO_PHASES


def test_init_state(tmp_path):
    """新建项目应创建 state.json，phase=init。"""
    sm = StateManager(tmp_path)
    sm.init(video_id="v_001", config={"type": "knowledge"})

    state_file = tmp_path / ".video" / "state.json"
    assert state_file.exists()
    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert data["phase"] == "init"
    assert data["video_id"] == "v_001"
    assert data["config"] == {"type": "knowledge"}
    assert "init" in data["phases_completed"]


def test_phase_progression(tmp_path):
    """phase 应能 init→write→review→visual→done 顺序推进。"""
    sm = StateManager(tmp_path)
    sm.init(video_id="v_001", config={})
    sm.set_phase("write")
    assert sm.current_phase() == "write"
    sm.set_phase("review")
    assert sm.current_phase() == "review"
    sm.set_phase("visual")
    assert sm.current_phase() == "visual"
    sm.set_phase("done")
    assert sm.current_phase() == "done"


def test_block_skip_from_init_to_visual(tmp_path):
    """从 init 跳到 visual 应被阻止（必须先经过 write/review）。"""
    sm = StateManager(tmp_path)
    sm.init(video_id="v_001", config={})
    with pytest.raises(InvalidTransition):
        sm.set_phase("visual")


def test_allow_jump_from_done(tmp_path):
    """phase=done 时可重跑任意 phase（标记 re_run=true）。"""
    sm = StateManager(tmp_path)
    sm.init(video_id="v_001", config={})
    sm.set_phase("write")
    sm.set_phase("review")
    sm.set_phase("visual")
    sm.set_phase("done")

    sm.set_phase("visual")  # 不应抛异常
    assert sm.current_phase() == "visual"
    state = sm.read()
    assert state["re_run"] is True


def test_phases_completed_accumulates(tmp_path):
    """phases_completed 应累积，不重复。"""
    sm = StateManager(tmp_path)
    sm.init(video_id="v_001", config={})
    sm.set_phase("write")
    sm.set_phase("review")
    state = sm.read()
    assert state["phases_completed"] == ["init", "write", "review"]


def test_video_phases_constant():
    """VIDEO_PHASES 包含 5 个 phase。"""
    assert VIDEO_PHASES == ["init", "write", "review", "visual", "done"]
