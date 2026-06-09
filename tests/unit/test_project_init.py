"""测试 project_init.py：创建视频项目目录结构。"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from project_init import init_project, ProjectExistsError


def test_init_creates_directory_layout(tmp_path):
    """init_project 应创建 设定/ 台本/ 素材/ 后期/ 发布/ + .video/。"""
    project = init_project(
        project_root=str(tmp_path / "my_video"),
        video_id="v_001",
        config={"type": "knowledge", "platform": "douyin"},
    )
    project = Path(project)

    assert (project / "设定").is_dir()
    assert (project / "台本").is_dir()
    assert (project / "素材").is_dir()
    assert (project / "素材" / "角色").is_dir()
    assert (project / "素材" / "场景").is_dir()
    assert (project / "素材" / "道具").is_dir()
    assert (project / "素材" / "视频").is_dir()
    assert (project / "素材" / "封面").is_dir()
    assert (project / "后期").is_dir()
    assert (project / "发布").is_dir()
    assert (project / ".video").is_dir()
    assert (project / ".video" / "state.json").is_file()


def test_init_refuses_existing_project(tmp_path):
    """如果项目目录已存在且含 .video/state.json，应抛 ProjectExistsError。"""
    project = tmp_path / "existing"
    project.mkdir()
    (project / ".video").mkdir()
    (project / ".video" / "state.json").write_text('{"phase": "init"}', encoding="utf-8")

    with pytest.raises(ProjectExistsError):
        init_project(
            project_root=str(project),
            video_id="v_002",
            config={},
        )


def test_init_returns_absolute_path(tmp_path):
    """init_project 返回绝对路径。"""
    project = init_project(
        project_root=str(tmp_path / "another"),
        video_id="v_003",
        config={},
    )
    assert Path(project).is_absolute()
