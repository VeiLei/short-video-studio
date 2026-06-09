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
