"""端到端测试：模拟整个 5-skill 流程，mock 所有后端调用。

目的：验证插件脚本、state machine、JSON schema、subtitle、publish 之间的集成。
不验证：Claude 创意决策、真实 Seedance 输出。
"""
import json
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from state_manager import StateManager
from project_init import init_project
from video_prompt_schema import validate_video_prompt
from subtitle_gen import parse_narration_to_srt, write_srt
from publish_export import export_publish_package

FIXTURES = ROOT / "tests" / "fixtures"


@pytest.fixture
def project(tmp_path):
    """创建测试用项目结构。"""
    project_path = init_project(
        project_root=str(tmp_path / "test_video"),
        video_id="v_test_001",
        config={"type": "knowledge", "platform": "douyin", "duration_sec": 30},
    )
    return Path(project_path)


def test_init_phase_creates_layout(project):
    """init 阶段应创建完整目录结构。"""
    assert (project / "设定").is_dir()
    assert (project / "台本").is_dir()
    assert (project / "素材" / "视频").is_dir()
    assert (project / "后期").is_dir()
    assert (project / "发布").is_dir()
    assert (project / ".video" / "state.json").is_file()


def test_write_phase_produces_valid_prompt(project):
    """write 阶段生成的视频提示词应通过 schema 校验。"""
    # 模拟 write 阶段产物
    prompt = {
        "video_id": "v_test_001",
        "title": "测试视频",
        "type": "knowledge",
        "target_platform": "douyin",
        "aspect_ratio": "9:16",
        "total_duration_sec": 30,
        "shots": [
            {
                "shot_id": "S01",
                "order": 1,
                "narration": "测试口播",
                "prompt": "测试画面 prompt",
                "video_params": {"duration_sec": 5, "aspect_ratio": "9:16"},
            }
        ]
    }
    prompt_file = project / "台本" / "视频提示词.json"
    prompt_file.parent.mkdir(exist_ok=True)
    prompt_file.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")

    # 校验
    data = json.loads(prompt_file.read_text(encoding="utf-8"))
    validate_video_prompt(data)  # 不抛

    # state 推进
    StateManager(str(project)).set_phase("write")
    assert StateManager(str(project)).current_phase() == "write"


def test_visual_phase_creates_video_files(project):
    """visual 阶段应在 素材/视频/ 放置 mp4 文件（mock 拷贝）。"""
    # 模拟 visual 阶段：拷贝 fixture
    for i in range(1, 4):
        (project / "素材" / "视频" / f"S0{i}.mp4").write_bytes(
            (FIXTURES / "mock_seedance.mp4").read_bytes()
        )

    videos = sorted((project / "素材" / "视频").glob("S*.mp4"))
    assert len(videos) == 3
    assert all(v.stat().st_size > 0 for v in videos)


def test_finish_phase_subtitle_and_publish(project):
    """finish 阶段应生成字幕、调用 publish_export。"""
    # 准备口播词
    narration = """# 测试视频

[00:00.000 → 00:03.000]
第一句口播。

[00:03.000 → 00:07.000]
第二句口播。
"""
    (project / "台本" / "口播词.md").write_text(narration, encoding="utf-8")

    # 生成字幕
    cues = parse_narration_to_srt(narration)
    srt_path = project / "后期" / "字幕.srt"
    write_srt(cues, path=str(srt_path))
    assert srt_path.exists()
    assert "00:00:00,000 --> 00:00:03,000" in srt_path.read_text(encoding="utf-8")

    # 准备封面
    cover_src = project / "素材" / "封面" / "封面.png"
    cover_src.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURES / "mock_jimeng.png", cover_src)

    # 导出发布包
    export_publish_package(
        project_root=str(project),
        video_meta={
            "title": "测试视频",
            "description": "测试描述",
            "tags": ["test", "AI"],
            "platforms": ["douyin", "xiaohongshu"],
        },
        cover_source=str(cover_src),
    )

    assert (project / "发布" / "标题与描述.txt").exists()
    assert (project / "发布" / "标签.json").exists()
    assert (project / "发布" / "元数据.json").exists()
    assert (project / "发布" / "发布清单.md").exists()
    assert (project / "发布" / "cover.png").exists()

    # state 推进（模拟经过所有阶段）
    sm = StateManager(str(project))
    sm.set_phase("write")
    sm.set_phase("review")
    sm.set_phase("visual")
    sm.set_phase("done")
    assert sm.current_phase() == "done"


def test_state_machine_blocks_skip(project):
    """state machine 阻止非法跳跃。"""
    from state_manager import InvalidTransition
    sm = StateManager(str(project))
    # 当前 phase=init，不应能跳到 visual
    with pytest.raises(InvalidTransition):
        sm.set_phase("visual")
