"""创建新的视频项目目录结构。

调用 StateManager.init 初始化 state.json。
"""

import sys
from pathlib import Path

# 让脚本可以独立运行
sys.path.insert(0, str(Path(__file__).parent))
from state_manager import StateManager


class ProjectExistsError(Exception):
    """项目已存在（含 .video/state.json）。"""


DIRECTORIES = [
    "设定",
    "台本",
    "素材/角色",
    "素材/场景",
    "素材/道具",
    "素材/视频",
    "素材/封面",
    "后期",
    "发布",
    ".video",
]


def init_project(project_root: str, video_id: str, config: dict) -> str:
    """创建视频项目目录结构并初始化 state.json。

    Args:
        project_root: 项目根目录路径。
        video_id: 视频唯一 ID。
        config: 配置 dict（如 type、platform、duration_sec）。

    Returns:
        绝对路径字符串。

    Raises:
        ProjectExistsError: 项目目录已存在且含 .video/state.json。
    """
    project_path = Path(project_root).resolve()
    state_file = project_path / ".video" / "state.json"

    if state_file.exists():
        raise ProjectExistsError(
            f"Project already initialized: {state_file}"
        )

    for sub in DIRECTORIES:
        (project_path / sub).mkdir(parents=True, exist_ok=True)

    sm = StateManager(project_path)
    sm.init(video_id=video_id, config=config)

    return str(project_path)
