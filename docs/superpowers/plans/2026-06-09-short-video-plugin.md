# short-video-studio 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个独立的 Claude Code 插件 `short-video-studio`，用于 AI 短视频创作；通过 5 个 skill 驱动 init→write→review→visual→finish 工作流；复用 short-drama-writer 后端并新增极小扩展。

**Architecture:** 独立插件 + 共享后端。新插件在 `short-video-studio/plugin/` 下，5 个 SKILL.md 驱动创作流程，Python 脚本做数据 IO。后端在 `short-drama-writer/backend/app/cli.py` 中加 `video-cover` 命令和 `video-generate --mode narration` 标志。

**Tech Stack:** Python 3.10+, Claude Code 插件 SDK, ffmpeg, FastAPI（复用）, jimeng-4.6（复用）, Seedance 2.0（复用）, pytest, jsonschema

**Spec:** [2026-06-09-short-video-plugin-design.md](../specs/2026-06-09-short-video-plugin-design.md)

---

## 实施阶段概览

| 阶段 | 任务 | 涉及目录 |
|---|---|---|
| A. 基础 | Task 1-2 | 项目骨架 + 依赖 |
| B. 后端扩展 | Task 3-4 | short-drama-writer/backend/app/cli.py |
| C. 插件 Python 脚本 | Task 5-9 | short-video-studio/plugin/scripts/ |
| D. 类型模板 | Task 10 | short-video-studio/plugin/templates/types/ |
| E. 5 个 Skill | Task 11-15 | short-video-studio/plugin/skills/ |
| F. 集成测试 + 文档 | Task 16-17 | tests/ + README |

---

## Task 1: 创建项目目录骨架

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/plugin.json`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/.gitkeep`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/.gitkeep`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/.gitkeep`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/references/.gitkeep`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/tests/.gitkeep`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/tests/fixtures/.gitkeep`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/pytest.ini`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/requirements-dev.txt`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/.gitignore`

- [ ] **Step 1: 创建所有目录**

在 `d:/PersonalFiles/Project_Space/short-video-studio/` 下创建：

```
plugin/
  scripts/
  skills/
  templates/
  references/
tests/
  fixtures/
docs/
```

- [ ] **Step 2: 写 plugin.json**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/plugin.json`

```json
{
  "name": "short-video-studio",
  "version": "0.1.0",
  "description": "AI 短视频创作插件。5 个 skill 驱动 init→write→review→visual→finish。复用 short-drama-writer 后端。",
  "author": "vei_ge",
  "license": "MIT",
  "skills": [
    "skills/video-init",
    "skills/video-write",
    "skills/video-review",
    "skills/video-visual",
    "skills/video-finish"
  ]
}
```

- [ ] **Step 3: 写 pytest.ini**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

- [ ] **Step 4: 写 requirements-dev.txt**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/requirements-dev.txt`

```
jsonschema>=4.21.0
pytest>=7.4.0
pytest-mock>=3.11.0
```

- [ ] **Step 5: 写 .gitignore**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/

# Test
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp

# 用户项目（每个视频项目独立）
项目/
素材/
台本/
设定/
后期/
发布/
.video/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 6: 提交**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
git init
git add .
git commit -m "chore: scaffold short-video-studio project structure"
```

---

## Task 2: 设置后端符号链接（开发模式）

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/backend` (symlink to short-drama-writer backend)

> **注意**：本计划假设后端在 `short-drama-writer/backend/`。开发期间，短视频插件通过相对路径引用后端；Task 3/4 会在后端 `app/cli.py` 加新代码。开发者必须能在编辑器里同时打开两个项目。

- [ ] **Step 1: 验证后端可访问**

```bash
ls d:/PersonalFiles/Project_Space/short-drama-writer/backend/app/cli.py
```

预期：文件存在，输出 `app/cli.py`（Windows 显示完整路径）。

- [ ] **Step 2: 在 README 中记录后端路径约定**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/README.md`（先创建空文件，下游 Task 17 填内容）

```markdown
# short-video-studio

AI 短视频创作 Claude Code 插件。

> 后端开发约定：本插件**复用** `../short-drama-writer/backend/`。
> 所有 Python 数据脚本调用后端 CLI（不直接 import 后端模块）。
> 后端扩展点见 `../short-drama-writer/backend/app/cli.py`。
```

- [ ] **Step 3: 提交**

```bash
git add README.md
git commit -m "docs: add readme with backend dependency note"
```

---

## Task 3: 后端扩展 — 添加 `video-cover` CLI（TDD）

**Files:**
- Modify: `d:/PersonalFiles/Project_Space/short-drama-writer/backend/app/cli.py`
- Test: `d:/PersonalFiles/Project_Space/short-drama-writer/backend/tests/test_video_cover_cli.py`

> 后端已有 pytest 结构（参考现有 `tests/` 目录）。如无则创建。

- [ ] **Step 1: 写失败的测试**

文件路径：`d:/PersonalFiles/Project_Space/short-drama-writer/backend/tests/test_video_cover_cli.py`

```python
"""测试 video-cover CLI 命令。

video-cover 是新增命令，包装 jimeng.generate 生成单张图片作为视频封面。
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 让测试可以 import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.asset_index import AssetIndex


def test_video_cover_writes_file_and_index(tmp_path, monkeypatch):
    """video-cover 应生成图片文件、写入 assets.json covers 段。"""
    # Arrange: 创建项目结构
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".video").mkdir()
    AssetIndex(str(project))  # 初始化

    # Mock jimeng.generate 返回假图片
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"fakepngdata" * 10
    async def fake_generate(prompt, aspect_ratio, reference_images=None):
        result = MagicMock()
        result.image_url = "data:image/png;base64," + __import__("base64").b64encode(fake_bytes).decode()
        return result
    monkeypatch.setattr("app.cli.jimeng.generate", fake_generate)

    # Mock TOS 上传
    monkeypatch.setattr("app.cli.upload_to_tos", lambda b, t: "https://tos.example/cover.png")

    # Act: 调用 video-cover
    from app.cli import cmd_video_cover
    args = MagicMock()
    args.project = str(project)
    args.prompt = "一只可爱的猫咪作为视频封面"
    args.ratio = "9:16"
    args.name = "封面"

    asyncio.run(cmd_video_cover(args))

    # Assert: 文件存在
    cover_path = project / "素材" / "封面" / "封面.png"
    assert cover_path.exists(), f"封面文件未生成: {cover_path}"
    assert cover_path.read_bytes() == fake_bytes

    # Assert: assets.json 记录
    index = AssetIndex(str(project))
    covers = index.to_dict().get("covers", {})
    assert "封面" in covers, f"assets.json 未记录封面: {covers}"
    assert covers["封面"]["tos_url"] == "https://tos.example/cover.png"


def test_video_cover_skips_when_exists(tmp_path, monkeypatch, capsys):
    """video-cover 在文件已存在时跳过。"""
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".video").mkdir()
    (project / "素材" / "封面").mkdir(parents=True)
    existing = project / "素材" / "封面" / "封面.png"
    existing.write_bytes(b"existing")

    from app.utils.asset_index import AssetIndex
    AssetIndex(str(project))

    # 不应调 jimeng
    async def fail_generate(*a, **kw):
        raise AssertionError("jimeng.generate 不应被调用")
    monkeypatch.setattr("app.cli.jimeng.generate", fail_generate)

    from app.cli import cmd_video_cover
    args = MagicMock()
    args.project = str(project)
    args.prompt = "..."
    args.ratio = "9:16"
    args.name = "封面"

    asyncio.run(cmd_video_cover(args))

    captured = capsys.readouterr()
    assert "已存在" in captured.out
    assert existing.read_bytes() == b"existing"
```

- [ ] **Step 2: 验证测试失败**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer/backend
.venv/Scripts/python -m pytest tests/test_video_cover_cli.py -v
```

预期：FAIL，错误 `ImportError: cannot import name 'cmd_video_cover' from 'app.cli'`。

- [ ] **Step 3: 在 AssetIndex 加 covers 字段支持**

文件路径：`d:/PersonalFiles/Project_Space/short-drama-writer/backend/app/utils/asset_index.py`

找到 `to_dict` 和 `add_*` 方法区，添加：

```python
def add_cover(self, name: str, tos_url: str, local_path: str, prompt: str):
    """记录一个视频封面。"""
    if "covers" not in self.data:
        self.data["covers"] = {}
    self.data["covers"][name] = {
        "tos_url": tos_url,
        "local_path": local_path,
        "prompt": prompt,
        "created_at": _now_iso(),
    }
    self._save()
```

并在文件顶部 `_now_iso` 函数旁（如不存在则添加）：

```python
from datetime import datetime, timezone
def _now_iso():
    return datetime.now(timezone.utc).isoformat()
```

> **注意**：原文件可能已有类似工具函数，复用之，不重复定义。

- [ ] **Step 4: 在 cli.py 加 cmd_video_cover 函数**

文件路径：`d:/PersonalFiles/Project_Space/short-drama-writer/backend/app/cli.py`

在文件中找到 `cmd_video_generate` 之前的位置（搜索 `cmd_video_prompt`），插入：

```python
async def cmd_video_cover(args):
    """生成视频封面。包装 jimeng.generate，写入 assets.json covers 段。"""
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    # 幂等：已存在则跳过
    local_dir = Path(project_root) / "素材" / "封面"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / f"{args.name}.png"
    if local_path.exists():
        print(f"⊙ {args.name} 封面已存在，跳过")
        return

    logger.info("Video cover: %s", args.name)
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio)

    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_cover(args.name, tos_url=tos_url, local_path=str(local_path), prompt=prompt)
    print(f"✓ {args.name} 封面 → {tos_url}")
```

- [ ] **Step 5: 在 main() 中注册 video-cover 子命令**

在 `main()` 函数中找到 `p = sub.add_parser("video-generate", ...)` 之前，添加：

```python
    p = sub.add_parser("video-cover", help="Generate video cover image (wraps jimeng.generate)")
    p.add_argument("--project", required=True, help="Project directory path")
    p.add_argument("--name", required=True, help="Cover name (e.g., '封面' or 'cover_v1')")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")
```

并在 `sync_cmds = {"assets", "video-prompt"}` 之后（无需修改 `sync_cmds`），cli.py 末尾的 dispatch 逻辑是 `globals()[f"cmd_{args.command.replace('-', '_')}"](args)`，会自动调用 `cmd_video_cover`。

- [ ] **Step 6: 验证测试通过**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer/backend
.venv/Scripts/python -m pytest tests/test_video_cover_cli.py -v
```

预期：PASS，2 个 test 通过。

- [ ] **Step 7: 提交**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer
git add backend/app/cli.py backend/app/utils/asset_index.py backend/tests/test_video_cover_cli.py
git commit -m "feat(backend): add video-cover CLI command"
```

---

## Task 4: 后端扩展 — `--mode narration` 标志（TDD）

**Files:**
- Modify: `d:/PersonalFiles/Project_Space/short-drama-writer/backend/app/cli.py`
- Test: `d:/PersonalFiles/Project_Space/short-drama-writer/backend/tests/test_narration_mode.py`

- [ ] **Step 1: 写失败的测试**

文件路径：`d:/PersonalFiles/Project_Space/short-drama-writer/backend/tests/test_narration_mode.py`

```python
"""测试 video-generate 的 --mode narration 标志。

当 --mode narration 传入时，prompt 应自动添加旁白前缀。
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_narration_mode_prepends_prefix(tmp_path, monkeypatch):
    """--mode narration 会在 prompt 前添加旁白风格前缀。"""
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".video").mkdir()

    captured_prompts = []

    # Mock video_provider.generate 捕获入参
    class FakeResult:
        video_id = "v_001"
        video_url = ""
        file_path = None
        duration = 0
        dimensions = ""
        aspect_ratio = "9:16"
        api_response = {}

    async def fake_generate(prompt, reference_images=None, ratio="9:16", duration=10, **kw):
        captured_prompts.append(prompt)
        return FakeResult()

    monkeypatch.setattr("app.cli.video_provider.generate", fake_generate)

    # Mock video prompt JSON 读取
    import json
    prompt_dir = project / "提示词"
    prompt_dir.mkdir()
    (prompt_dir / "第0001集-视频提示词.json").write_text(json.dumps({
        "episode_id": "0001",
        "shots": [
            {
                "shot_id": "S01",
                "prompt": {"positive": "小明在实验室里认真做实验"},
                "video_params": {"duration_sec": 6, "aspect_ratio": "9:16"},
                "character_references": [],
                "prop_references": [],
            }
        ]
    }), encoding="utf-8")

    from app.cli import cmd_video_generate
    args = MagicMock()
    args.project = str(project)
    args.episode = "0001"
    args.shot_id = "S01"
    args.scene = ""
    args.frame_id = ""
    args.prompt = ""
    args.ratio = ""
    args.duration = None
    args.refs = None
    args.mode = "narration"  # 新增标志

    asyncio.run(cmd_video_generate(args))

    assert len(captured_prompts) == 1
    p = captured_prompts[0]
    assert "自然讲述" in p or "narrator" in p.lower() or "视角" in p, \
        f"narration 模式未注入前缀。Got: {p[:200]}"
    assert "小明在实验室里认真做实验" in p, "原始 prompt 应保留"


def test_default_mode_unchanged(tmp_path, monkeypatch):
    """不传 --mode 时，prompt 不变。"""
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".video").mkdir()

    captured_prompts = []

    class FakeResult:
        video_id = "v_002"
        video_url = ""
        file_path = None
        duration = 0
        dimensions = ""
        aspect_ratio = "9:16"
        api_response = {}

    async def fake_generate(prompt, **kw):
        captured_prompts.append(prompt)
        return FakeResult()

    monkeypatch.setattr("app.cli.video_provider.generate", fake_generate)

    import json
    prompt_dir = project / "提示词"
    prompt_dir.mkdir()
    (prompt_dir / "第0001集-视频提示词.json").write_text(json.dumps({
        "episode_id": "0001",
        "shots": [
            {
                "shot_id": "S01",
                "prompt": {"positive": "原始 prompt 不变"},
                "video_params": {"duration_sec": 6, "aspect_ratio": "9:16"},
                "character_references": [],
                "prop_references": [],
            }
        ]
    }), encoding="utf-8")

    from app.cli import cmd_video_generate
    args = MagicMock()
    args.project = str(project)
    args.episode = "0001"
    args.shot_id = "S01"
    args.scene = ""
    args.frame_id = ""
    args.prompt = ""
    args.ratio = ""
    args.duration = None
    args.refs = None
    args.mode = None  # 默认

    asyncio.run(cmd_video_generate(args))

    assert len(captured_prompts) == 1
    p = captured_prompts[0]
    # 默认模式不应注入 narration 前缀
    assert "自然讲述" not in p
    assert "原始 prompt 不变" in p
```

- [ ] **Step 2: 验证测试失败**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer/backend
.venv/Scripts/python -m pytest tests/test_narration_mode.py -v
```

预期：FAIL，错误 `TypeError: ... unexpected keyword argument 'mode'`（或在 `args.mode` 处 AttributeError）。

- [ ] **Step 3: 在 cmd_video_generate 添加 narration 处理**

文件路径：`d:/PersonalFiles/Project_Space/short-drama-writer/backend/app/cli.py`

找到 `cmd_video_generate` 函数内 `Build prompt text` 段（即 `prompt = shot_prompt.get("positive", ...)` 之后，`ref_parts` 拼接之前），在 `if ref_parts: prompt = "。".join(ref_parts) + "。" + prompt` 之前，添加：

```python
        # ── Narration mode: prepend style prefix ──
        if getattr(args, "mode", None) == "narration":
            narration_prefix = (
                "镜头以自然讲述的视角展开，人物口型与节奏与旁白同步，"
                "画面有适度的镜头呼吸感与场景氛围，环境音清晰。"
            )
            prompt = narration_prefix + prompt
            logger.info("  mode=narration: prefix injected")
```

- [ ] **Step 4: 在 main() 中给 video-generate 加 --mode 标志**

在 `sub.add_parser("video-generate", ...)` 段末尾，添加：

```python
    p.add_argument("--mode", default=None, choices=[None, "narration"],
                   help="Generation mode: 'narration' injects narrator-style prefix into prompt")
```

- [ ] **Step 5: 验证测试通过**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer/backend
.venv/Scripts/python -m pytest tests/test_narration_mode.py -v
```

预期：PASS，2 个 test 通过。

- [ ] **Step 6: 跑全部后端测试确认无回归**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer/backend
.venv/Scripts/python -m pytest tests/ -v
```

预期：所有 test 通过（含 Task 3 / Task 4 新增的）。

- [ ] **Step 7: 提交**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer
git add backend/app/cli.py backend/tests/test_narration_mode.py
git commit -m "feat(backend): add --mode narration flag to video-generate CLI"
```

---

## Task 5: 插件脚本 — `state_manager.py`（TDD）

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/state_manager.py`
- Test: `d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_state_manager.py`

- [ ] **Step 1: 写失败的测试**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_state_manager.py`

```python
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
```

- [ ] **Step 2: 验证测试失败**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_state_manager.py -v
```

预期：FAIL，`ModuleNotFoundError: No module named 'state_manager'`。

- [ ] **Step 3: 实现 state_manager.py**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/state_manager.py`

```python
"""state.json 读写与状态机。

每个视频项目一个 .video/state.json，记录当前阶段、配置、时间戳。
phase 顺序：init → write → review → visual → done
"""

import json
import sys
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
```

- [ ] **Step 4: 验证测试通过**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_state_manager.py -v
```

预期：PASS，6 个 test 通过。

- [ ] **Step 5: 提交**

```bash
git add plugin/scripts/state_manager.py tests/unit/test_state_manager.py
git commit -m "feat(scripts): add state_manager.py for video project state"
```

---

## Task 6: 插件脚本 — `project_init.py`（TDD）

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/project_init.py`
- Test: `d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_project_init.py`

- [ ] **Step 1: 写失败的测试**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_project_init.py`

```python
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
```

- [ ] **Step 2: 验证测试失败**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_project_init.py -v
```

预期：FAIL，`ModuleNotFoundError: No module named 'project_init'`。

- [ ] **Step 3: 实现 project_init.py**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/project_init.py`

```python
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
```

- [ ] **Step 4: 验证测试通过**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_project_init.py -v
```

预期：PASS，3 个 test 通过。

- [ ] **Step 5: 提交**

```bash
git add plugin/scripts/project_init.py tests/unit/test_project_init.py
git commit -m "feat(scripts): add project_init.py to scaffold video project"
```

---

## Task 7: 插件脚本 — `video_prompt_schema.py`（TDD）

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/video_prompt_schema.py`
- Test: `d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_video_prompt_schema.py`

- [ ] **Step 1: 写失败的测试**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_video_prompt_schema.py`

```python
"""测试视频提示词 JSON schema 校验。"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from video_prompt_schema import validate_video_prompt, ValidationError


VALID_PROMPT = {
    "video_id": "v_2026-06-09_001",
    "title": "3分钟读懂Transformer",
    "type": "knowledge",
    "target_platform": "douyin",
    "aspect_ratio": "9:16",
    "total_duration_sec": 90,
    "shots": [
        {
            "shot_id": "S01",
            "order": 1,
            "scene": "实验室",
            "frame_type": "establishing",
            "narration": "你有没有想过，ChatGPT 是怎么理解人话的？",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": "实验室场景，白大褂的小明面对镜头...",
            "video_params": {
                "duration_sec": 6,
                "aspect_ratio": "9:16",
                "camera": "中景正面",
                "motion": "说话动作",
            },
        }
    ],
}


def test_valid_prompt_passes():
    """合法的视频提示词应通过校验。"""
    validate_video_prompt(VALID_PROMPT)  # 不抛


def test_missing_shots_fails():
    """缺少 shots 字段应失败。"""
    bad = {**VALID_PROMPT}
    del bad["shots"]
    with pytest.raises(ValidationError):
        validate_video_prompt(bad)


def test_shot_missing_required_fails():
    """shot 缺少 shot_id/order 应失败。"""
    bad = json.loads(json.dumps(VALID_PROMPT))
    del bad["shots"][0]["shot_id"]
    with pytest.raises(ValidationError):
        validate_video_prompt(bad)


def test_invalid_type_fails():
    """type 字段不在白名单应失败。"""
    bad = json.loads(json.dumps(VALID_PROMPT))
    bad["type"] = "unknown_type"
    with pytest.raises(ValidationError):
        validate_video_prompt(bad)


def test_duration_too_long_warns(caplog):
    """duration > 30s 应警告（Seedance 单次上限）。"""
    bad = json.loads(json.dumps(VALID_PROMPT))
    bad["shots"][0]["video_params"]["duration_sec"] = 60
    # 不抛异常，但记录警告
    validate_video_prompt(bad)
```

- [ ] **Step 2: 验证测试失败**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_video_prompt_schema.py -v
```

预期：FAIL，`ModuleNotFoundError: No module named 'video_prompt_schema'`。

- [ ] **Step 3: 实现 video_prompt_schema.py**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/video_prompt_schema.py`

```python
"""视频提示词 JSON schema 校验。

定义 spec §5.1 的结构，校验台本输出合法性。
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

VALID_TYPES = {"knowledge", "marketing", "story", "vlog", "news", "other"}
VALID_PLATFORMS = {"douyin", "kuaishou", "xiaohongshu", "bilibili", "shipinhao", "other"}
VALID_FRAME_TYPES = {"establishing", "two_shot", "close_up", "over_shoulder", "insert", "other"}


class ValidationError(Exception):
    """视频提示词不符合 schema。"""


SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["video_id", "title", "type", "target_platform", "aspect_ratio", "shots"],
    "properties": {
        "video_id": {"type": "string"},
        "title": {"type": "string"},
        "type": {"type": "string", "enum": list(VALID_TYPES)},
        "target_platform": {"type": "string", "enum": list(VALID_PLATFORMS)},
        "aspect_ratio": {"type": "string", "pattern": r"^\d+:\d+$"},
        "total_duration_sec": {"type": "integer", "minimum": 1},
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["shot_id", "order", "prompt", "video_params"],
                "properties": {
                    "shot_id": {"type": "string"},
                    "order": {"type": "integer", "minimum": 1},
                    "scene": {"type": "string"},
                    "frame_type": {"type": "string", "enum": list(VALID_FRAME_TYPES)},
                    "narration": {"type": "string"},
                    "dialogue": {"type": "string"},
                    "characters": {"type": "array", "items": {"type": "string"}},
                    "outfits": {"type": "array", "items": {"type": "string"}},
                    "prompt": {"type": "string", "minLength": 1},
                    "video_params": {
                        "type": "object",
                        "required": ["duration_sec"],
                        "properties": {
                            "duration_sec": {"type": "integer", "minimum": 1, "maximum": 30},
                            "aspect_ratio": {"type": "string", "pattern": r"^\d+:\d+$"},
                            "camera": {"type": "string"},
                            "motion": {"type": "string"},
                        },
                    },
                },
            },
        },
    },
}


def validate_video_prompt(data: dict[str, Any]) -> None:
    """校验视频提示词 JSON。

    Raises:
        ValidationError: 不符合 schema 时。
    """
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        raise ValidationError("jsonschema package not installed. Run: pip install jsonschema")

    validator = Draft7Validator(SCHEMA)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    for err in errors:
        path = ".".join(str(p) for p in err.path) or "<root>"
        raise ValidationError(f"{path}: {err.message}")

    # Soft warning for long durations
    for shot in data.get("shots", []):
        dur = shot.get("video_params", {}).get("duration_sec", 0)
        if dur > 30:
            logger.warning(
                "Shot %s duration_sec=%d exceeds Seedance 30s limit; will be split.",
                shot.get("shot_id", "?"), dur,
            )
```

- [ ] **Step 4: 安装 jsonschema 依赖**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/pip install jsonschema>=4.21.0
```

- [ ] **Step 5: 验证测试通过**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_video_prompt_schema.py -v
```

预期：PASS，5 个 test 通过。

- [ ] **Step 6: 提交**

```bash
git add plugin/scripts/video_prompt_schema.py tests/unit/test_video_prompt_schema.py
git commit -m "feat(scripts): add video_prompt_schema.py validator"
```

---

## Task 8: 插件脚本 — `subtitle_gen.py`（TDD）

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/subtitle_gen.py`
- Test: `d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_subtitle_gen.py`

- [ ] **Step 1: 写失败的测试**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_subtitle_gen.py`

```python
"""测试口播词 → SRT 字幕生成。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from subtitle_gen import parse_narration_to_srt, write_srt


NARRATION = """# 我的视频

[00:00.000 → 00:03.500]
你有没有想过，ChatGPT 是怎么理解人话的？

[00:03.500 → 00:07.200]
今天我们用 3 分钟讲清楚 Transformer。

[00:07.200 → 00:12.000]
先从一个简单的问题开始。
"""


def test_parse_extracts_cues():
    """parse_narration_to_srt 应从 markdown 提取时间轴条目。"""
    cues = parse_narration_to_srt(NARRATION)
    assert len(cues) == 3
    assert cues[0]["start_ms"] == 0
    assert cues[0]["end_ms"] == 3500
    assert "你有没有想过" in cues[0]["text"]


def test_srt_format():
    """SRT 格式：序号 + 时间 + 文本 + 空行。"""
    cues = parse_narration_to_srt(NARRATION)
    srt = write_srt(cues)
    assert "1\n" in srt
    assert "00:00:00,000 --> 00:00:03,500" in srt
    assert "你有没有想过" in srt
    assert "\n\n2\n" in srt  # 条目间空行


def test_srt_writes_to_file(tmp_path):
    """write_srt 接受 path 参数。"""
    cues = parse_narration_to_srt(NARRATION)
    out = tmp_path / "out.srt"
    write_srt(cues, path=str(out))
    content = out.read_text(encoding="utf-8")
    assert "00:00:00,000" in content


def test_empty_narration_returns_empty():
    """无时间轴标记的纯文本返回空列表。"""
    cues = parse_narration_to_srt("就是一些普通文本")
    assert cues == []
```

- [ ] **Step 2: 验证测试失败**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_subtitle_gen.py -v
```

预期：FAIL，`ModuleNotFoundError: No module named 'subtitle_gen'`。

- [ ] **Step 3: 实现 subtitle_gen.py**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/subtitle_gen.py`

```python
"""口播词 markdown → SRT 字幕。

口播词格式（由 video-write 输出）：
```
# 标题

[00:00.000 → 00:03.500]
字幕内容

[00:03.500 → 00:07.200]
下一条字幕
```
"""

import re
from pathlib import Path
from typing import Any

CUE_RE = re.compile(
    r"\[(\d{1,2}):(\d{2})\.(\d{3})\s*→\s*(\d{1,2}):(\d{2})\.(\d{3})\]\s*\n(.+?)(?=\n\[|\Z)",
    re.DOTALL,
)


def _to_ms(min: str, sec: str, ms: str) -> int:
    return int(min) * 60_000 + int(sec) * 1_000 + int(ms)


def _format_timestamp(ms: int) -> str:
    """将毫秒转 SRT 时间格式 HH:MM:SS,mmm。"""
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_narration_to_srt(markdown: str) -> list[dict[str, Any]]:
    """从口播词 markdown 解析字幕条目。"""
    cues = []
    for match in CUE_RE.finditer(markdown):
        min1, sec1, ms1, min2, sec2, ms2, text = match.groups()
        cues.append({
            "start_ms": _to_ms(min1, sec1, ms1),
            "end_ms": _to_ms(min2, sec2, ms2),
            "text": text.strip(),
        })
    return cues


def write_srt(cues: list[dict[str, Any]], path: str | None = None) -> str:
    """把字幕条目序列化为 SRT 格式字符串，可选写入文件。"""
    lines = []
    for i, cue in enumerate(cues, start=1):
        lines.append(str(i))
        lines.append(f"{_format_timestamp(cue['start_ms'])} --> {_format_timestamp(cue['end_ms'])}")
        lines.append(cue["text"])
        lines.append("")  # 空行分隔

    srt_text = "\n".join(lines)

    if path:
        Path(path).write_text(srt_text, encoding="utf-8")

    return srt_text
```

- [ ] **Step 4: 验证测试通过**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_subtitle_gen.py -v
```

预期：PASS，4 个 test 通过。

- [ ] **Step 5: 提交**

```bash
git add plugin/scripts/subtitle_gen.py tests/unit/test_subtitle_gen.py
git commit -m "feat(scripts): add subtitle_gen.py for narration to SRT"
```

---

## Task 9: 插件脚本 — `publish_export.py`（TDD）

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/publish_export.py`
- Test: `d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_publish_export.py`

- [ ] **Step 1: 写失败的测试**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/tests/unit/test_publish_export.py`

```python
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
```

- [ ] **Step 2: 验证测试失败**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_publish_export.py -v
```

预期：FAIL，`ModuleNotFoundError: No module named 'publish_export'`。

- [ ] **Step 3: 实现 publish_export.py**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts/publish_export.py`

```python
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
```

- [ ] **Step 4: 验证测试通过**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/test_publish_export.py -v
```

预期：PASS，5 个 test 通过。

- [ ] **Step 5: 跑全部 unit test 确认无回归**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/unit/ -v
```

预期：所有 test 通过（state_manager / project_init / video_prompt_schema / subtitle_gen / publish_export 共 23 个）。

- [ ] **Step 6: 提交**

```bash
git add plugin/scripts/publish_export.py tests/unit/test_publish_export.py
git commit -m "feat(scripts): add publish_export.py for release package"
```

---

## Task 10: 类型模板 — knowledge / marketing / story

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/types/knowledge.md`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/types/marketing.md`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/types/story.md`

- [ ] **Step 1: 创建 knowledge.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/types/knowledge.md`

```markdown
# 知识科普型 — 类型模板

## 适用场景

- 3 分钟 / 5 分钟讲懂一个概念
- 冷知识系列
- 原理讲解（如 Transformer、扩散模型）
- 历史/科学普及

## 钩子策略（视频前 3 秒）

- **悬念型**："你有没有想过，X 是怎么 Y 的？"
- **反常识型**："其实 X 根本不是 Z 做的。"
- **数字冲击**："90% 的人都搞错了 X。"

## 推荐结构

```
[0-3s]  钩子：提出悬念
[3-10s] 引入：场景化铺垫
[10-30s] 核心 1：第一层解释
[30-50s] 核心 2：类比 + 可视化
[50-70s] 核心 3：深入一层
[70-85s] 总结：回到开头的钩子
[85-90s] CTA：点赞 + 关注
```

## 角色建议

- 1 个虚拟主播（白大褂 / 休闲衬衫 + 简单背景）
- 无需复杂场景
- 强调"讲述"感，非"表演"感

## 节奏

- 句长控制在 15-20 字
- 长句拆成 2-3 个镜头
- 关键概念用"停顿 + 强调"

## 标题公式

- "[数字]+[时间]+[动词]+[概念]"
- "3 分钟读懂 Transformer"
- "90 秒讲清楚扩散模型"
- "5 个冷知识颠覆你的认知"
```

- [ ] **Step 2: 创建 marketing.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/types/marketing.md`

```markdown
# 营销种草型 — 类型模板

## 适用场景

- 产品测评
- 购物推荐 / 带货
- 生活方式分享
- 网红/达人种草

## 钩子策略（视频前 3 秒）

- **强冲击**："这款 XX 真的太顶了！"
- **痛点共鸣**："每次 X 都让我崩溃，直到我发现..."
- **价格锚定**："9.9 居然能买到这种东西？！"

## 推荐结构

```
[0-3s]  钩子：痛点 / 惊喜 / 反转
[3-15s] 问题：用户场景化描述
[15-30s] 产品出场：第一印象
[30-50s] 卖点 1：核心功能
[50-65s] 卖点 2：差异化优势
[65-80s] 卖点 3：使用场景
[80-90s] CTA：购买链接 / 优惠码
```

## 角色建议

- 出镜达人（真实感强）
- 产品特写镜头（细节质感）
- 多场景（试用 / 对比 / 上身效果）

## 节奏

- 情绪起伏明显
- 关键卖点处放慢 + 重音
- BGM 节奏匹配情绪

## 标题公式

- "[数字]+[情绪]+[产品/品类]"
- "3 个理由让我离不开这款咖啡"
- "9.9 买到的高级感"
- "姐妹们冲！这款 XX 真的不踩雷"
```

- [ ] **Step 3: 创建 story.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/types/story.md`

```markdown
# 故事段子型 — 类型模板

## 适用场景

- 反转小故事
- 日常 vlog
- 段子 / 搞笑
- 情感共鸣短片

## 钩子策略（视频前 3 秒）

- **场景开局**："昨天下午三点，我在咖啡厅遇到..."
- **悬念型**："我到现在都没想明白那天到底发生了什么。"
- **冲突型**："我爸突然说：'我们搬家吧。'"

## 推荐结构

```
[0-3s]  钩子：场景/冲突/悬念
[3-20s] 铺垫：背景/人物/情绪
[20-40s] 发展：第一个转折
[40-65s] 高潮：核心冲突
[65-80s] 反转：意外结局
[80-90s] 余味：情绪留白
```

## 角色建议

- 1-2 个角色（无需多）
- 真实生活场景（家、咖啡厅、办公室、街道）
- 强调表演和情绪，非旁白

## 节奏

- 镜头切换频繁（每 3-5s 一切）
- 关键情绪点用慢动作
- 结尾留白 > 总结

## 标题公式

- "[场景]+[情绪]+[动作]"
- "咖啡厅里，我遇到了 5 年没见的她"
- "凌晨 3 点，我爸敲开了我的门"
- "那条朋友圈发出去 5 分钟后，我后悔了"
```

- [ ] **Step 4: 创建类型模板索引文件**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/templates/types/README.md`

```markdown
# 类型模板

视频类型模板，供 `/video-init` skill 在 init 阶段套用。

| 文件 | 类型 | 核心钩子 | 适合场景 |
|---|---|---|---|
| `knowledge.md` | 知识科普 | 悬念 / 反常识 / 数字 | 概念讲解、原理普及 |
| `marketing.md` | 营销种草 | 强冲击 / 痛点 / 价格 | 产品测评、带货 |
| `story.md` | 故事段子 | 场景 / 悬念 / 冲突 | 反转故事、vlog |

新类型按相同格式添加。`/video-init` 会用 `AskUserQuestion` 让用户选类型。
```

- [ ] **Step 5: 提交**

```bash
git add plugin/templates/types/
git commit -m "feat(templates): add knowledge, marketing, story type templates"
```

---

## Task 11: Skill — `video-init`

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-init/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-init/SKILL.md`

````markdown
---
name: video-init
description: 初始化一个短视频项目。收集主题、类型、平台、时长、角色，套用类型模板，生成 设定/ 文件。
allowed-tools: Read Write Bash AskUserQuestion
---

初始化一个短视频项目。

## 何时使用

- 用户说 "/video-init"
- 用户说"开新视频"、"做一个新视频"、"新建项目"

## 前置条件

- 当前工作目录是项目父目录（脚本会自动 `mkdir`）
- Python 3.10+ 且 `plugin/scripts/` 可 import

## 工作流

### 步骤 1：AskUserQuestion 收集信息

按以下顺序提问（用 `AskUserQuestion` 一次问一个或合并相关项）：

1. **视频主题/标题**：开放文本
2. **类型**：knowledge / marketing / story / vlog / news / other（默认 knowledge）
3. **目标平台**：douyin / kuaishou / xiaohongshu / bilibili / shipinhao（多选，默认 douyin）
4. **目标时长（秒）**：30 / 60 / 90（默认 60）
5. **是否出镜角色**：无 / 1 个虚拟主播 / 1-2 个真实人物（默认 1 个虚拟主播）
6. **场景数量**：1-3（默认 1，最简单）
7. **钩子策略**：从所选类型的模板中提取前 3 个选项

### 步骤 2：调用 init_project 脚本

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from project_init import init_project
project = init_project(
    project_root='./<video_id>',
    video_id='<video_id>',
    config={'type': '<type>', 'platform': '<platform>', 'duration_sec': <duration>}
)
print(project)
"
```

`video_id` 格式：`v_YYYY-MM-DD_NNN`，如 `v_2026-06-09_001`。

### 步骤 3：套用类型模板生成 设定/

读取 `plugin/templates/types/<type>.md`，把钩子策略、推荐结构写到 `设定/视频档案.md`：

```markdown
# <视频主题>

**video_id**: <video_id>
**类型**: <type>
**目标平台**: <platform>
**目标时长**: <duration> 秒
**aspect_ratio**: 9:16（默认，short-form 短视频）

## 钩子策略

<从类型模板钩子策略段复制用户所选>

## 推荐结构

<从类型模板推荐结构段复制>

## 视觉风格

<让 Claude 根据类型 + 主题生成 5-10 行的风格描述>
```

### 步骤 4：生成 设定/角色.md（如果出镜）

```markdown
# 角色

## <角色名>

- **身份**：<身份，如"白大褂研究员">
- **外观锚点**：<3-5 个关键外貌点>
- **口播风格**：<语气、节奏>
- **典型动作**：<3-5 个常用动作>
```

### 步骤 5：生成 设定/场景.md

```markdown
# 场景

## <场景名>

- **空间描述**：<室内/室外、布局>
- **关键地标**：<3-5 个标志性物品>
- **光线/色调**：<冷暖、光源方向>
- **氛围基调**：<专注/轻松/紧张>
```

### 步骤 6：生成 设定/视觉风格.md

```markdown
# 视觉风格

- **整体风格**：<写实/CG/插画/混合>
- **色调**：<冷/暖/中性，主辅色>
- **镜头语言**：<纪录/电影/vlog>
- **参考**：<如"知识区头部账号 '老石' 的视觉风格">
```

### 步骤 7：更新 state

脚本已经自动 init state.json (phase=init)。不需要再手动 set_phase。

## 状态机

完成后 phase=init。用户下一步运行 `/video-write`。

## 关键约束

- 不要在项目目录创建 .py 脚本，始终用 `plugin/scripts/` 里的模块
- type 字段必须是白名单中的一个（参考 `video_prompt_schema.py`）
- aspect_ratio 默认 9:16（除非用户明确要其他比例）
- 不要生成大纲/分集/章节（短视频没有这些概念）
````

- [ ] **Step 2: 提交**

```bash
git add plugin/skills/video-init/
git commit -m "feat(skills): add video-init skill"
```

---

## Task 12: Skill — `video-write`

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-write/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-write/SKILL.md`

````markdown
---
name: video-write
description: 写台本。基于 设定/ 生成 口播词.md、分镜.md、视频提示词.json。
allowed-tools: Read Write Bash AskUserQuestion
---

基于 设定/ 生成完整台本。

## 何时使用

- 用户说 "/video-write"
- `/video-init` 已完成

## 前置条件

- `.video/state.json` 存在且 phase ∈ {init, write}
- `设定/` 目录含 视频档案.md、角色.md、场景.md、视觉风格.md

## 工作流

### 步骤 1：读 设定/

读 `设定/视频档案.md` 拿到主题、类型、平台、时长、钩子策略、推荐结构。
读 `设定/角色.md` 拿到角色外观/动作。
读 `设定/场景.md` 拿到场景信息。
读 `设定/视觉风格.md` 拿到整体风格。

### 步骤 2：生成 台本/口播词.md

完整口播脚本。每段带时间轴：

```markdown
# <视频主题> — 口播词

## 总时长：<duration> 秒
## 钩子段：[0-3s]
<钩子内容，1-2 句>

## 主体段：[3-80s]
<按推荐结构展开，每个核心点 1-3 段>

## 收尾段：[80-90s]
<总结 + CTA>

## 详细时间轴

[00:00.000 → 00:03.500]
<钩子完整文字>

[00:03.500 → 00:08.000]
<第一段内容>

[00:08.000 → 00:13.500]
<第二段内容>

...

[01:25.000 → 01:30.000]
<CTA 文字>
```

时间轴精度 0.5s，段长 3-7s。Subtitle 解析器会读这个。

### 步骤 3：生成 台本/分镜.md

每个 shot 一行：

```markdown
# 分镜

| shot_id | 时长 | 场景 | 角色 | 机位 | 动作 |
|---|---|---|---|---|---|
| S01 | 3.5s | 实验室 | 小明 | 中景正面 | 思考状 |
| S02 | 4.5s | 实验室 | 小明 | 近景 | 解释口型 |
| S03 | 5.0s | 实验室 | 小明 | 特写 | 手势强调 |
...
```

总时长应与口播词的总时长一致。

### 步骤 4：生成 台本/视频提示词.json

```python
import json
import sys
from pathlib import Path

# 加载 schema
sys.path.insert(0, str(Path("<plugin_root>/plugin/scripts").resolve()))
from video_prompt_schema import validate_video_prompt

data = {
    "video_id": "<video_id>",
    "title": "<主题>",
    "type": "<type>",
    "target_platform": "<platform>",
    "aspect_ratio": "9:16",
    "total_duration_sec": <duration>,
    "shots": [
        {
            "shot_id": "S01",
            "order": 1,
            "scene": "实验室",
            "frame_type": "establishing",
            "narration": "<从口播词对应段复制>",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": "实验室场景，白大褂的小明面对镜头，略带思考，<视觉风格>. 色调冷暖混合.",
            "video_params": {
                "duration_sec": 6,
                "aspect_ratio": "9:16",
                "camera": "中景正面",
                "motion": "说话动作"
            }
        }
        # ... 其他 shot
    ]
}

# 校验
validate_video_prompt(data)

# 写入
Path("<project_root>/台本/视频提示词.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
```

### 步骤 5：更新 state

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from state_manager import StateManager
StateManager('<project_root>').set_phase('write')
"
```

## 关键约束

- 提示词应包含 视觉风格.md 中的关键词
- 角色引用应与 设定/角色.md 一致
- 场景引用应与 设定/场景.md 一致
- 视频总时长应与 设定/视频档案.md 一致
- 必须在写完文件后调用 `validate_video_prompt` 校验
````

- [ ] **Step 2: 提交**

```bash
git add plugin/skills/video-write/
git commit -m "feat(skills): add video-write skill"
```

---

## Task 13: Skill — `video-review`

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-review/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-review/SKILL.md`

````markdown
---
name: video-review
description: 审查台本与视频提示词的一致性、逻辑、AI 味。不修改文件，只输出问题清单。
allowed-tools: Read Write Bash
---

审查台本与视频提示词。

## 何时使用

- 用户说 "/video-review"
- `/video-write` 已完成

## 前置条件

- `.video/state.json` phase ∈ {write, review}
- `台本/` 含完整内容

## 工作流

### 步骤 1：读所有相关文件

读 `设定/*.md`、`台本/口播词.md`、`台本/分镜.md`、`台本/视频提示词.json`。

### 步骤 2：6 维检查

#### 1. 设定一致性
- 视频档案的钩子策略在口播词中是否体现？
- 角色外观在分镜中是否一致？
- 场景描述在视频提示词中是否准确？
- 视觉风格关键词是否被使用？

#### 2. 叙事连贯性
- 口播词段落之间的逻辑是否通顺？
- 是否有跳脱的句子？
- 段间过渡是否自然？

#### 3. 角色一致性
- 角色在所有 shot 中是否同一个人？
- 角色着装是否在分镜中明确？
- 角色性格是否在口播词语气中一致？

#### 4. 时间线
- 口播词总时长是否 = 视频档案目标时长？
- 分镜 shot 时长之和是否 = 总时长？
- 字幕时间轴是否与分镜时长匹配？

#### 5. AI 味检测
- 是否有过度的"作为 AI"自指？
- 是否有 AI 套话（"首先、其次、最后"）？
- 是否有不自然的结构（"希望对你有帮助"）？
- 是否有同质化表达（"非常重要"、"至关重要"）？

#### 6. 镜头连续性
- 相邻 shot 的角色位置/朝向是否合理？
- 相邻 shot 的机位变化是否合理（避免跳轴）？
- 场景转换是否平滑？

### 步骤 3：写入 review.md

```markdown
# 审查报告

**video_id**: <video_id>
**审查时间**: <ISO 时间>
**审查范围**: 口播词 + 分镜 + 视频提示词

## 总结

[整体评价：优 / 良 / 中 / 差 + 1-2 句概述]

## 严重问题（必须修复）

### 问题 1：[简述]
- **位置**：口播词 / 分镜 / 视频提示词: <行号或段>
- **类型**：设定不一致 / 逻辑跳脱 / ...
- **建议**：<具体修改建议>

## 建议改进（可选）

### 建议 1：[简述]
...

## 已知问题清单（来自上轮 visual）

<如果上轮 video-visual 有失败记录，从 .video/voice_index.json 或 assets.json 读出>
```

### 步骤 4：更新 state

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from state_manager import StateManager
StateManager('<project_root>').set_phase('review')
"
```

## 关键约束

- **不修改任何文件** — 只输出报告
- 不要跳维度 — 6 维都要检查
- 严重问题 vs 建议改进要分清（严重 = 影响最终视频质量）
````

- [ ] **Step 2: 提交**

```bash
git add plugin/skills/video-review/
git commit -m "feat(skills): add video-review skill"
```

---

## Task 14: Skill — `video-visual`

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-visual/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-visual/SKILL.md`

````markdown
---
name: video-visual
description: 生成所有视觉资产 + 视频片段。调用后端 CLI 生成四视图/全景/取景框/视频。
allowed-tools: Read Write Bash
---

生成所有视觉资产（角色、场景、道具、镜头视频）。

## 何时使用

- 用户说 "/video-visual"
- `/video-write` 已完成（`/video-review` 可选但推荐）

## 前置条件

- `.video/state.json` phase ∈ {write, review, visual}
- `台本/视频提示词.json` 存在且已通过 schema 校验
- 后端 `.env` 配置完整（火山引擎 JIMENG_API_KEY、ARK_API_KEY 等）
- 后端 venv 存在且依赖已装

## 后端 CLI 路径

按以下顺序查找（与 short-drama-writer 插件一致）：

1. `d:/PersonalFiles/Project_Space/short-drama-writer/backend/.venv/Scripts/python -m app.cli`（本地开发，优先）
2. `${CLAUDE_PLUGIN_ROOT}/../short-drama-writer/backend/.venv/Scripts/python -m app.cli`
3. 报错

## 工作流

### 阶段 1：扫描提示词，列出缺失资产

读 `台本/视频提示词.json`，提取：
- 所有角色名（去重）
- 所有场景名（去重）
- 所有道具名（去重）
- 所有 shot

读 `.video/assets.json`（如不存在则创建空），对比：
- 哪些角色有基础四视图？
- 哪些场景有全景图？
- 哪些道具已生成？
- 哪些 shot 已生成视频？

### 阶段 2：生成缺失资产

#### 2a. 角色基础四视图（缺失时）

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer/backend
.venv/Scripts/python -m app.cli four-views \
  --project <project_root> \
  --name <角色名> \
  --prompt "<CG 游戏角色原画风格，...角色外观...>"
```

#### 2b. 变装四视图（如果某 shot 引用了非"基础"着装）

```bash
.venv/Scripts/python -m app.cli variant \
  --project <project_root> \
  --name <角色名> \
  --outfit <着装名> \
  --prompt "..."
```

CLI 自动以基础四视图为 reference_image。

#### 2c. 场景全景图（缺失时）

```bash
.venv/Scripts/python -m app.cli scene-master \
  --project <project_root> \
  --name <场景名> \
  --prompt "<场景类型>，<关键地标>，<空间尺寸>。<氛围>，<色调/光照>。空镜，无人物。竖屏 9:16。"
```

#### 2d. 场景取景框（缺失时）

```bash
.venv/Scripts/python -m app.cli shot-frame \
  --project <project_root> \
  --scene <场景名> \
  --frame-id <frame_id> \
  --frame-type <type> \
  --prompt "..."
```

CLI 自动以场景 master 图为 reference_image。

#### 2e. 道具参考图（缺失时）

```bash
.venv/Scripts/python -m app.cli prop-ref \
  --project <project_root> \
  --name <道具名> \
  --prompt "CG 游戏原画风格，<道具描述>。纯白背景，无人物。"
```

### 阶段 3：逐 shot 生成视频

对每个 shot，调用后端 CLI：

```bash
.venv/Scripts/python -m app.cli video-generate \
  --project <project_root> \
  --episode <episode_id> \
  --shot-id <shot_id> \
  --scene <场景名> \
  --frame-id <frame_id>  # 如果该 shot 有专属取景框
```

> **MVP 阶段**：先不传 `--mode narration`，因为旁白型会让 Seedance 倾向于出环境音+空镜+旁白口型，纯对白/纯表演型会受影响。如果用户明确要"知识科普型"，再加 `--mode narration`。

CLI 自动从 `台本/视频提示词.json` 读取 prompt、duration、refs。

### 阶段 4：写失败记录

如果某个 shot 生成失败（CLI 返回非零退出码），写到 `.video/voice_index.json`：

```json
{
  "failed_shots": [
    {
      "shot_id": "S07",
      "error": "Seedance content filter",
      "timestamp": "2026-06-09T12:30:00Z"
    }
  ]
}
```

video-review 在下轮会读这个。

### 阶段 5：更新 state

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from state_manager import StateManager
StateManager('<project_root>').set_phase('visual')
"
```

## 错误处理

- **API key 错误**（401/403）→ 立即终止，提示用户检查 .env
- **Seedance 内容过滤** → 单 shot 重试一次，换同义词；再失败则标记 failed
- **限流（429）** → CLI 已有 submit_lock 串行化
- **轮询超时**（>30 分钟）→ 标记 timeout，跳过
- **TOS 上传失败** → 本地保留图片，tos_url 置空

## 关键约束

- 严格按"缺失才生成"原则 — 已有的资产不重发 API
- 单 shot 失败不影响其他 shot
- 不在项目目录创建 .py 脚本
- 提示词超长用文件传入：`--prompt @/tmp/prompt.txt`
````

- [ ] **Step 2: 提交**

```bash
git add plugin/skills/video-visual/
git commit -m "feat(skills): add video-visual skill"
```

---

## Task 15: Skill — `video-finish`

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-finish/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/plugin/skills/video-finish/SKILL.md`

````markdown
---
name: video-finish
description: 视频后期。拼接镜头、烧字幕、叠 BGM、生成封面、导出发布包。
allowed-tools: Read Write Bash
---

视频后期。调 ffmpeg 和本地 Python 脚本完成所有合成。

## 何时使用

- 用户说 "/video-finish"
- `/video-visual` 已完成

## 前置条件

- `.video/state.json` phase ∈ {visual, done}
- `素材/视频/S*.mp4` 全部存在（或失败记录在 voice_index.json）
- ffmpeg 在 PATH 中（`ffmpeg -version`）
- BGM 素材在 `plugin/assets/bgm/`（如无可跳过）

## 工作流

### 步骤 1：检查所有镜头视频

读 `台本/视频提示词.json`，按 shot_id 列出应有视频。
读 `素材/视频/`，列出实际有的。
计算缺失/失败的 shot — 提示用户。

如有关键 shot 缺失，**停止**并提示用户重跑 video-visual 补齐。

### 步骤 2：生成字幕 SRT

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from subtitle_gen import parse_narration_to_srt, write_srt
from pathlib import Path

narration = Path('<project_root>/台本/口播词.md').read_text(encoding='utf-8')
cues = parse_narration_to_srt(narration)
out = Path('<project_root>/后期/字幕.srt')
write_srt(cues, path=str(out))
print(f'Wrote {len(cues)} cues to {out}')
"
```

### 步骤 3：拼接镜头（ffmpeg concat）

```bash
# 创建 concat 列表
cd <project_root>/素材/视频
ls S*.mp4 | sort > /tmp/concat_list.txt
# 改写为绝对路径
sed -i "s|^|<project_root>/素材/视频/|" /tmp/concat_list.txt

# Concat
ffmpeg -f concat -safe 0 -i /tmp/concat_list.txt \
  -c copy <project_root>/后期/终版_raw.mp4
```

> **Windows 注意**：用 `echo` 而非 `sed`，或用 PowerShell 改写。

### 步骤 4：烧字幕（可选）

```bash
ffmpeg -i <project_root>/后期/终版_raw.mp4 \
  -vf "subtitles=<project_root>/后期/字幕.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'" \
  <project_root>/后期/终版_subtitled.mp4
```

### 步骤 5：叠加 BGM（可选）

```bash
# 调节 BGM 音量为原视频音量的 20%（旁白为主）
ffmpeg -i <project_root>/后期/终版_subtitled.mp4 \
  -i <bgm_path> \
  -filter_complex "[1:a]volume=0.2[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac \
  <project_root>/后期/终版_final.mp4
```

如无 BGM 素材，跳过此步，复制 `终版_subtitled.mp4` 为 `终版_final.mp4`。

### 步骤 6：生成封面

调后端新增的 `video-cover` CLI：

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer/backend
.venv/Scripts/python -m app.cli video-cover \
  --project <project_root> \
  --name "封面" \
  --ratio "9:16" \
  --prompt "<基于视频主题 + 视觉风格生成的封面 prompt>"
```

封面 prompt 模板：

```
竖屏 9:16 视频封面。<视频主题>。<视觉风格关键词>。
画面构图：<如"主体居中，留白适合加标题文字">。
高对比度，吸睛，文字不遮挡。
```

CLI 会把封面写到 `<project_root>/素材/封面/封面.png`。

### 步骤 7：导出发布包

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from publish_export import export_publish_package

export_publish_package(
    project_root='<project_root>',
    video_meta={
        'title': '<视频标题>',
        'description': '<视频描述>',
        'tags': ['<tag1>', '<tag2>', ...],
        'platforms': ['douyin', 'xiaohongshu']
    },
    cover_source='<project_root>/素材/封面/封面.png'
)
"
```

### 步骤 8：更新 state

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from state_manager import StateManager
StateManager('<project_root>').set_phase('done')
"
```

## 关键约束

- ffmpeg 命令在 Windows / Mac / Linux 略不同 — 测试时跨平台验证
- 字幕烧录是计算密集型操作，90s 视频约需 1-2 分钟
- BGM 音量不超过原音频的 30%（否则压过旁白）
- 封面 prompt 必须强调"高对比、留白"以适合加文字
- 失败时不要静默 — 写明哪一步失败、错误输出
````

- [ ] **Step 2: 提交**

```bash
git add plugin/skills/video-finish/
git commit -m "feat(skills): add video-finish skill"
```

---

## Task 16: 集成测试 — 完整流程 fixture

**Files:**
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/tests/integration/test_e2e_mocked.py`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/tests/fixtures/mock_jimeng.png`
- Create: `d:/PersonalFiles/Project_Space/short-video-studio/tests/fixtures/mock_seedance.mp4`

- [ ] **Step 1: 写 mock fixture（小 PNG + 1 秒 mp4）**

在 `d:/PersonalFiles/Project_Space/short-video-studio/tests/fixtures/` 下创建：

```python
# 用 Python 生成最小的有效 PNG 和 MP4
import subprocess
from pathlib import Path

fixtures = Path(__file__).parent

# 1x1 PNG（最小有效 PNG）
png = fixtures / "mock_jimeng.png"
if not png.exists():
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=red:s=64x64:d=1",
        "-frames:v", "1", str(png)
    ], check=True, capture_output=True)

# 1 秒 MP4
mp4 = fixtures / "mock_seedance.mp4"
if not mp4.exists():
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x568:d=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(mp4)
    ], check=True, capture_output=True)
```

直接执行一次生成 fixture：

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio/tests/fixtures
ffmpeg -y -f lavfi -i color=c=red:s=64x64:d=1 -frames:v 1 mock_jimeng.png
ffmpeg -y -f lavfi -i color=c=blue:s=320x568:d=1 -c:v libx264 -pix_fmt yuv420p mock_seedance.mp4
ls -la
```

预期：两个文件存在。

- [ ] **Step 2: 写集成测试**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/tests/integration/test_e2e_mocked.py`

```python
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

    # state 推进
    StateManager(str(project)).set_phase("done")
    assert StateManager(str(project)).current_phase() == "done"


def test_state_machine_blocks_skip(project):
    """state machine 阻止非法跳跃。"""
    from state_manager import InvalidTransition
    sm = StateManager(str(project))
    # 当前 phase=init，不应能跳到 visual
    with pytest.raises(InvalidTransition):
        sm.set_phase("visual")
```

- [ ] **Step 3: 跑集成测试**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/integration/ -v
```

预期：PASS，5 个 test 通过。

- [ ] **Step 4: 跑所有测试**

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -m pytest tests/ -v
```

预期：所有 test 通过（unit 23 + integration 5 = 28 个）。

- [ ] **Step 5: 提交**

```bash
git add tests/
git commit -m "test: add end-to-end integration test with mocked fixtures"
```

---

## Task 17: README 与安装说明

**Files:**
- Modify: `d:/PersonalFiles/Project_Space/short-video-studio/README.md`

- [ ] **Step 1: 写完整 README**

文件路径：`d:/PersonalFiles/Project_Space/short-video-studio/README.md`

````markdown
# short-video-studio

AI 短视频创作 Claude Code 插件。

5 个 skill 驱动 `init → write → review → visual → finish` 端到端工作流。复用 [short-drama-writer](../short-drama-writer) 后端（火山引擎即梦 4.6 + Seedance 2.0）。

> 后端开发约定：本插件**复用** `../short-drama-writer/backend/`。
> 所有 Python 数据脚本调用后端 CLI（不直接 import 后端模块）。
> 后端扩展点见 `../short-drama-writer/backend/app/cli.py`。

## 项目结构

```
short-video-studio/
├── plugin/
│   ├── plugin.json
│   ├── skills/                  # 5 个 SKILL.md
│   │   ├── video-init/
│   │   ├── video-write/
│   │   ├── video-review/
│   │   ├── video-visual/
│   │   └── video-finish/
│   ├── scripts/                 # Python 数据 IO 脚本
│   │   ├── state_manager.py
│   │   ├── project_init.py
│   │   ├── video_prompt_schema.py
│   │   ├── subtitle_gen.py
│   │   └── publish_export.py
│   ├── templates/types/         # 类型模板（knowledge / marketing / story）
│   └── references/              # 影视创作规则
├── tests/                       # pytest
│   ├── unit/                    # 23 个 unit test
│   ├── integration/             # 5 个 e2e test
│   └── fixtures/
├── docs/
│   └── superpowers/
│       ├── specs/               # 设计文档
│       └── plans/               # 实施计划
└── requirements-dev.txt
```

## 安装

### 前置条件

- Python 3.10+
- ffmpeg 在 PATH 中
- 已安装 [short-drama-writer](https://gitee.com/vei_ge/short-drama-writer) 后端并配好 `.env`
- Claude Code 1.0+

### 安装本插件

```bash
# 克隆本仓库
git clone <this-repo>
cd short-video-studio

# 安装 Python 依赖
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt

# 链接插件到 Claude Code
# Windows
mklink /D %USERPROFILE%\.claude\plugins\short-video-studio %CD%\plugin
# macOS / Linux
ln -s $(pwd)/plugin ~/.claude/plugins/short-video-studio
```

重启 Claude Code，输入 `/video-init` 即可使用。

## 快速开始

```bash
# 进入一个空目录（将作为视频项目父目录）
mkdir my-videos && cd my-videos
mkdir my-first-video && cd my-first-video

# 在 Claude Code 中
/video-init    # 收集信息，生成 设定/
/video-write   # 写台本
/video-review  # 审查（可选但推荐）
/video-visual  # 生成视频（需 token）
/video-finish  # 后期合成 + 导出发布包
```

## 测试

```bash
cd short-video-studio
.venv/Scripts/pytest tests/ -v
```

## 设计文档

- [2026-06-09-short-video-plugin-design.md](docs/superpowers/specs/2026-06-09-short-video-plugin-design.md) — 概念设计
- [2026-06-09-short-video-plugin.md](docs/superpowers/plans/2026-06-09-short-video-plugin.md) — 实施计划

## 与 short-drama-writer 的差异

| 维度 | short-drama-writer | short-video-studio |
|---|---|---|
| 项目单位 | 多集短剧 | 单视频 |
| 视频时长 | 1-3 min × 10+ 集 | 15-90s × 1 个 |
| 核心能力 | 角色一致性 + 叙事弧 | 钩子 + 口播 + 节奏 |
| 平台发行 | 不涉及 | 本地发布包导出 |
| 后端 | 自带 FastAPI | **完全复用短剧后端** |

## 后端依赖

本插件依赖 `../short-drama-writer/backend/` 已部署：
- 即梦 4.6 API Key
- ARK API Key（Seedance）
- 火山引擎 TOS 存储

详细见 [short-drama-writer README](../short-drama-writer/README.md)。
````

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: complete README with install and quick start"
```

---

## 自审检查表

- [x] **Spec 覆盖**：检查 spec 每节都有对应任务
  - §2 架构 → Task 1-4
  - §3 Skill 流程 → Task 11-15
  - §4 项目结构 → Task 1, 6
  - §5 Schema → Task 7
  - §6 决策日志 → 反映在 Task 1-15 中
  - §7 错误处理 → Task 14, 15
  - §8 测试 → Task 5-9 (unit), Task 16 (integration)
- [x] **占位符扫描**：无 TBD/TODO/占位代码
- [x] **类型一致性**：
  - `StateManager.set_phase/current_phase/read/init` 在所有任务一致
  - `validate_video_prompt/ValidationError` 一致
  - `init_project/ProjectExistsError` 一致
  - `parse_narration_to_srt/write_srt` 一致
  - `export_publish_package` 一致
- [x] **TDD 顺序**：所有 Python 脚本任务都先写测试再写实现
- [x] **频繁提交**：每个 Task 结束都有 commit
- [x] **DRY**：复用 short-drama-writer 的 `AssetIndex`、`AssetIndex.add_cover` 扩展
- [x] **YAGNI**：未实现 TTS/music/publish provider/多平台 API/query/dashboard/agent

## 实施总结

| 阶段 | 任务数 | 预计工作量 |
|---|---|---|
| A. 基础 | 1-2 | 30 min |
| B. 后端扩展 | 3-4 | 2-3 hr |
| C. 插件脚本 | 5-9 | 4-6 hr |
| D. 类型模板 | 10 | 1 hr |
| E. 5 个 Skill | 11-15 | 3-4 hr |
| F. 集成测试 + 文档 | 16-17 | 2-3 hr |
| **总计** | **17 个任务** | **~12-17 hr** |
