"""测试发布包导出（封面 + 元数据 + 上传清单）。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from publish_export import export_publish_package


VIDEO_META = {
    "title": "3分钟读懂Transformer",
    "description": "用最简单的方式讲清楚 Transformer 架构。",
    "tags": ["AI", "深度学习", "科普", "Transformer"],
    "platforms": ["douyin", "xiaohongshu"],
}


def test_export_creates_directory_files(tmp_path):
    """export_publish_package 应在 发布/ 目录生成多个文件。"""
    # Arrange: 模拟项目结构
    project = tmp_path / "video"
    project.mkdir()
    (project / "发布").mkdir()
    (project / "后期").mkdir(parents=True)
    (project / "后期" / "封面.png").write_bytes(b"\x89PNG fake")

    # Act
    export_publish_package(
        project_root=str(project),
        video_meta=VIDEO_META,
        cover_source=str(project / "后期" / "封面.png"),
    )

    # Assert
    assert (project / "发布" / "标题与描述.txt").exists()
    assert (project / "发布" / "标签.json").exists()
    assert (project / "发布" / "元数据.json").exists()
    assert (project / "发布" / "发布清单.md").exists()


def test_export_writes_title_description(tmp_path):
    """标题与描述.txt 应包含 title 和 description。"""
    project = tmp_path / "v"
    project.mkdir()
    (project / "发布").mkdir()
    (project / "后期").mkdir(parents=True)
    (project / "后期" / "封面.png").write_bytes(b"x")

    export_publish_package(
        project_root=str(project),
        video_meta=VIDEO_META,
        cover_source=str(project / "后期" / "封面.png"),
    )

    text = (project / "发布" / "标题与描述.txt").read_text(encoding="utf-8")
    assert "3分钟读懂Transformer" in text
    assert "用最简单的方式讲清楚" in text


def test_export_writes_tags_json(tmp_path):
    """标签.json 应包含 tags 数组。"""
    project = tmp_path / "v"
    project.mkdir()
    (project / "发布").mkdir()
    (project / "后期").mkdir(parents=True)
    (project / "后期" / "封面.png").write_bytes(b"x")

    export_publish_package(
        project_root=str(project),
        video_meta=VIDEO_META,
        cover_source=str(project / "后期" / "封面.png"),
    )

    data = json.loads((project / "发布" / "标签.json").read_text(encoding="utf-8"))
    assert "AI" in data["tags"]


def test_export_checklist_mentions_platforms(tmp_path):
    """发布清单.md 应列出所有 platform。"""
    project = tmp_path / "v"
    project.mkdir()
    (project / "发布").mkdir()
    (project / "后期").mkdir(parents=True)
    (project / "后期" / "封面.png").write_bytes(b"x")

    export_publish_package(
        project_root=str(project),
        video_meta=VIDEO_META,
        cover_source=str(project / "后期" / "封面.png"),
    )

    checklist = (project / "发布" / "发布清单.md").read_text(encoding="utf-8")
    assert "douyin" in checklist
    assert "xiaohongshu" in checklist


def test_export_copies_cover(tmp_path):
    """封面应被复制到 发布/cover.png。"""
    project = tmp_path / "v"
    project.mkdir()
    (project / "发布").mkdir()
    cover_src = project / "后期" / "封面.png"
    cover_src.parent.mkdir(parents=True)
    cover_src.write_bytes(b"FAKE_COVER_BYTES")

    export_publish_package(
        project_root=str(project),
        video_meta=VIDEO_META,
        cover_source=str(cover_src),
    )

    copied = project / "发布" / "cover.png"
    assert copied.exists()
    assert copied.read_bytes() == b"FAKE_COVER_BYTES"
