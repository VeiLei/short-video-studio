"""导出发布包到 项目/发布/。

生成 4 个文件 + 1 张封面：
- 标题与描述.txt
- 标签.json
- 元数据.json
- 发布清单.md（人工上传 checklist）
- cover.png（封面副本）

不做平台 API 上传。用户在每个平台手动上传。
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


PLATFORM_GUIDES = {
    "douyin": "抖音：上传时选 9:16，时长 15-90s，标题前 15 字最关键，#话题 3-5 个。",
    "kuaishou": "快手：上传时选 9:16，封面吸睛，标题口语化。",
    "xiaohongshu": "小红书：上传时选 9:16，标题用 emoji，#话题 5-10 个。",
    "bilibili": "B站：上传时选 16:9 或 9:16，标题吸引点击，简介放链接。",
    "shipinhao": "视频号：上传时选 9:16，标题简洁，封面清楚。",
}


def export_publish_package(
    project_root: str,
    video_meta: dict,
    cover_source: str,
) -> None:
    """导出发布包到 <project_root>/发布/。

    Args:
        project_root: 项目根目录绝对路径。
        video_meta: 视频元数据 dict，必含 keys：
            - title: 视频标题
            - description: 视频描述
            - tags: 标签 list
            - platforms: 目标平台 list
        cover_source: 封面源文件路径（应已被复制或剪到 后期/封面.png）。
    """
    project = Path(project_root)
    publish_dir = project / "发布"
    publish_dir.mkdir(parents=True, exist_ok=True)

    # 1. 标题与描述.txt
    title_desc = (
        f"标题：{video_meta['title']}\n\n"
        f"描述：\n{video_meta['description']}\n"
    )
    (publish_dir / "标题与描述.txt").write_text(title_desc, encoding="utf-8")

    # 2. 标签.json
    tags_data = {"tags": video_meta.get("tags", [])}
    (publish_dir / "标签.json").write_text(
        json.dumps(tags_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 3. 元数据.json
    metadata = {
        "title": video_meta["title"],
        "description": video_meta["description"],
        "tags": video_meta.get("tags", []),
        "platforms": video_meta.get("platforms", []),
        "cover": "cover.png",
        "final_video": "终版.mp4",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "upload_method": "manual",
    }
    (publish_dir / "元数据.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 4. 发布清单.md
    checklist_lines = [
        "# 发布清单",
        "",
        f"**视频标题**：{video_meta['title']}",
        "",
        "## 上传步骤",
        "",
    ]
    for i, platform in enumerate(video_meta.get("platforms", []), start=1):
        guide = PLATFORM_GUIDES.get(platform, "参考平台官方帮助文档。")
        checklist_lines.append(f"### {i}. {platform}")
        checklist_lines.append(f"- {guide}")
        checklist_lines.append("- 上传 终版.mp4")
        checklist_lines.append("- 上传 cover.png 作为封面")
        checklist_lines.append("- 复制 标题与描述.txt 内容")
        checklist_lines.append("- 添加 标签.json 中的 # 标签")
        checklist_lines.append("")

    (publish_dir / "发布清单.md").write_text(
        "\n".join(checklist_lines), encoding="utf-8"
    )

    # 5. 复制封面
    if cover_source and Path(cover_source).exists():
        shutil.copy2(cover_source, publish_dir / "cover.png")
