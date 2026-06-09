# short-video-studio 插件 — 概念设计

**日期**：2026-06-09
**作者**：brainstorm 协作
**状态**：Draft，待用户审阅

---

## 1. 概述

### 1.1 目标

构建一个独立的 Claude Code 插件（`short-video-studio`），用于 AI 短视频创作。它与现有的 `short-drama-writer` 插件共享后端服务，但提供专门面向"单视频"工作流的创作流程、独特能力（语音/字幕/本地多平台变体/选题驱动/项目管理），并复用 Seedance 2.0 的原生音视频生成能力。

### 1.2 与 short-drama-writer 的关系

| 维度 | short-drama-writer | short-video-studio |
|---|---|---|
| 项目单位 | 多集短剧 | 单视频 |
| 视频时长 | 1-3 min × 10+ 集 | 15-90s × 1 个视频 |
| 核心能力 | 角色一致性 + 叙事弧 | 钩子 + 口播 + 节奏 |
| 后端 | FastAPI + MySQL + 火山引擎 | **完全复用短剧后端** |
| 插件 Skill 数 | 7 | 5（精简版） |
| 平台发行 | 不涉及 | 本地变体包导出（不调平台 API） |

两套插件可同时安装在同一台机器、同一后端，路由分离、互不污染。

### 1.3 核心差异点（独特能力）

1. **语音/口播/字幕** — 视频生成时同步处理，无需独立 TTS
2. **本地发布包导出** — 封面 + 元数据 + 上传清单（不调平台 API；不自动多比例裁剪）
3. **热点/选题驱动** — init 阶段支持从趋势/账号人设反推可拍内容
4. **多项目管理** — 暂不实现（YAGNI），项目粒度即单视频

> 详见 §6 设计决策日志。

---

## 2. 架构总览

### 2.1 目录与模块边界

```
short-drama-writer (existing)              short-video-studio (new)
┌──────────────────────────────┐           ┌──────────────────────────────┐
│ plugin/                     │           │ plugin/                     │
│  ├ skills/ (7)              │           │  ├ skills/ (5)              │
│  ├ agents/ (4)              │           │  ├ agents/ (TBD)            │
│  ├ genres/ (6)              │           │  ├ templates/ (类型模板)     │
│  └ scripts/                 │           │  └ scripts/                 │
└──────────────────────────────┘           └──────────────────────────────┘
              │                                       │
              └───────────────┬───────────────────────┘
                              ▼
              ┌──────────────────────────────┐
              │ short-drama-writer/backend/  │
              │  ├ image_providers/ (即梦)    │
              │  ├ video_providers/ (Seedance)│
              │  ├ api/generate.py           │
              │  ├ cli.py (新增 1-2 命令)    │
              │  └ utils/ (TOS / 资产索引)   │
              └──────────────────────────────┘
```

### 2.2 后端复用 vs 新增

**完全复用**（零修改）：
- `app/api/generate.py`（角色四视图、变装、全景、取景框、道具）
- `app/image_providers/jimeng46_adapter.py`（即梦 4.6）
- `app/video_providers/seedance_adapter.py`（Seedance 2.0）
- `app/utils/tos.py`、`app/utils/asset_index.py`

**新增（极小，< 50 行）**：
- `app/cli.py` 加 `video-cover` 命令（生成视频封面，包装 `jimeng.generate`）。**由 `video-finish` skill 在合成封面时调用**。
- `app/cli.py` `video-generate` 加 `--mode narration` 标志（在 prompt 前添加"镜头从 X 视角，自然讲述..."前缀）

**不新增**：
- TTS provider（Seedance 自带音频）
- 字幕 provider（本地脚本生成 srt）
- 音乐 provider（本地 ffmpeg 拼接）
- 发布 provider（仅导出文件）
- 多平台 provider（无 API 集成）
- **不新增 API 路由**：虽然命名上保留 `/api/shortvideo/*` 命名空间，但 MVP 阶段不实现任何新 REST 路由——所有交互走 CLI

### 2.3 与短剧后端共享的处理方式

- 单一后端部署
- CLI 命令命名空间：短剧命令不变（`four-views` 等）；短视频新增命令以 `video-` 前缀（`video-cover`）
- 两套插件用户在同一台机器可同时安装
- API 路由（如果未来加）：短剧用 `/api/generate/*`，短视频用 `/api/shortvideo/*` 命名空间隔离

---

## 3. Skill 协作流（5 个 skill 端到端）

### 3.1 总览

```
用户输入                    Claude + 插件               后端
─────────────────────────────────────────────────────────────────

/video-init                 AskUserQuestion 收集          (无后端调用)
  ↓                           ↓
  主题? 类型? 平台?           生成 设定/*.md
  时长? 出镜? 钩子策略?       生成 state.json (phase=init)
                              类型模板套用

/video-write                读 设定/                    (无后端调用)
  ↓                           ↓
  (用户可微调)                生成 口播词.md
                              生成 分镜.md (可能为空)
                              生成 视频提示词.json
                              state.json (phase=write)

/video-review                读 设定/ + 台本/ + 提示词/  (无后端调用)
  ↓                           ↓
                              6 维检查 (设定/叙事/角色/
                              时间线/AI味/镜头连续)
                              输出一致性问题清单 (不修改)

/video-visual                读 视频提示词.json           调 /api/generate/*
  ↓                           ↓                                  (角色/场景/道具，
  (用户确认开始)              缺失资产 → 生成四视图/             短剧既有路由)
                              全景/取景框/道具/视频            CLI video-generate
                              assets.json 索引                    (Seedance)
                              state.json (phase=visual)

/video-finish                读 口播词.md + 素材/视频/   CLI video-cover
  ↓                           ↓                                  (新加命令,包
  (用户确认)                  字幕 SRT 生成 + 烧录              装 jimeng)
                              BGM 叠加 (可跳过)                本地 ffmpeg
                              封面生成 → 调 video-cover
                              终版 mp4 输出
                              发布/ 目录导出
                              state.json (phase=done)
```

### 3.2 状态机

5 个 phase：`init` → `write` → `review` → `visual` → `done`

```
phase=init,write  → 调 visual  → 阻止（必须显式跳到 visual）
phase=visual      → 任意 phase → 允许
phase=done        → 任意 phase → 允许重跑（标记 re_run=true）
```

### 3.3 关键设计原则

1. **state.json 状态机**：5 个 phase，允许跳过 review（标记 `review_skipped=true`）但不建议
2. **幂等性**：每个 skill 重跑都先查 state，已完成的不重做；assets.json 同名资产跳过
3. **review 不修改文件**：只输出问题清单，用户自己改
4. **visual 是最重的 skill**：所有生成能力都集中在此
5. **finish 不调远端 AI**（除封面外）：纯本地 ffmpeg / 文本处理

### 3.4 视频生成的两个阶段

| 阶段 | Skill | 工具 | 产物 |
|---|---|---|---|
| 镜头级视频 | `video-visual` | Seedance 2.0 | 12 个独立 mp4（含音频） |
| 成片组装 | `video-finish` | ffmpeg 本地处理 | 1 个终版 mp4 |

Seedance 单次只能生成 5-10s，必须在 `video-finish` 中拼接。短剧的 `video-generate` CLI 直接复用。

---

## 4. 单视频项目结构

### 4.1 目录布局

```
我的视频项目/                     ← 用户新建的单个项目目录
├── .video/                       ← 状态/索引（gitignore）
│   ├── state.json                ← 状态机：当前阶段、已完成项
│   ├── assets.json               ← 资产索引（与短剧同名同结构）
│   └── voice_index.json          ← 语音/字幕/音乐索引
│
├── 设定/                          ← 由 video-init 生成
│   ├── 视频档案.md                ← 视频主题/类型/时长/平台/钩子策略
│   ├── 角色.md                    ← 角色列表（可能为空）
│   ├── 场景.md                    ← 场景列表（可能为空）
│   └── 视觉风格.md                ← 风格锚点
│
├── 台本/                          ← 由 video-write 生成
│   ├── 口播词.md                  ← 完整口播脚本
│   ├── 分镜.md                    ← 镜头列表（无人物时为空）
│   └── 视频提示词.json            ← Seedance 输入（结构同短剧）
│
├── 素材/                          ← 由 video-visual 生成
│   ├── 角色/
│   ├── 场景/
│   ├── 道具/
│   └── 视频/                      ← Seedance 输出 mp4
│
├── 后期/                          ← 由 video-finish 生成
│   ├── 字幕.srt                   ← 烧录用字幕
│   ├── 字幕烧录版.mp4             ← 可选烧录后版本
│   ├── 背景音乐.mp3               ← 选定的 BGM
│   ├── 终版.mp4                   ← 音视频合成终版
│   └── 封面.png                   ← 视频封面
│
└── 发布/                          ← 由 video-finish 导出
    ├── 发布清单.md                ← 各平台人工上传 checklist
    ├── 标题与描述.txt
    ├── 标签.json
    └── 元数据.json                ← 平台/账号/发布时间建议
```

### 4.2 与短剧项目的关键差异

- 短剧有"大纲"中间层，短视频合并到 `台本/`
- 短剧素材按集分目录，短视频全在 `素材/视频/`
- 短视频多 `后期/` 和 `发布/` 目录（短剧没有）
- `设定/` 内容可能极少（无角色时几行字）

---

## 5. 关键数据 Schema

### 5.1 视频提示词 JSON

这是最核心的中间数据，`video-write` 输出，`video-visual` 消费：

```json
{
  "video_id": "v_2026-06-09_001",
  "title": "3分钟读懂Transformer",
  "type": "knowledge",            // knowledge / marketing / story / ...
  "target_platform": "douyin",     // douyin / kuaishou / xiaohongshu / ...
  "aspect_ratio": "9:16",
  "total_duration_sec": 90,
  "shots": [
    {
      "shot_id": "S01",
      "order": 1,
      "scene": "实验室",            // 引用 设定/场景.md 中的场景
      "frame_type": "establishing",
      "dialogue": "",               // 旁白型：narration 字段；对话型：dialogue
      "narration": "你有没有想过，ChatGPT 是怎么理解人话的？",
      "characters": ["小明"],       // 引用 设定/角色.md
      "outfits": ["白大褂"],
      "prompt": "实验室场景，白大褂的小明面对镜头，略带思考...",
      "video_params": {
        "duration_sec": 6,
        "aspect_ratio": "9:16",
        "camera": "中景正面",
        "motion": "说话动作",
        "refs": ["scene_master_实验室.png", "小明_白大褂.png"]
      }
    }
  ]
}
```

### 5.2 state.json（状态机）

```json
{
  "video_id": "v_2026-06-09_001",
  "phase": "visual",               // init | write | review | visual | done
  "phases_completed": ["init", "write", "review"],
  "created_at": "2026-06-09T10:00:00",
  "updated_at": "2026-06-09T12:30:00",
  "config": {
    "type": "knowledge",
    "platform": "douyin",
    "duration_sec": 90
  }
}
```

### 5.3 assets.json

完全复用 short-drama-writer 的 `AssetIndex` schema（角色 variants、场景 master/shot_frames、道具）。短视频与短剧资产结构相同，索引工具零修改。

### 5.4 端到端一次走通的例子

```
用户: /video-init
  ↓ (Q&A: "3分钟读懂Transformer", 知识科普, 抖音, 90秒, 1个角色小明, 实验室场景)
  ↓
  Claude 写: 设定/视频档案.md, 设定/角色.md(小明), 设定/场景.md(实验室), 设定/视觉风格.md
  Claude 写: .video/state.json (phase=init)
  Claude 写: 类型模板套用 → 知识科普的钩子策略："3秒悬念 + 视觉冲击"

用户: /video-write
  ↓
  Claude 读 设定/，写: 台本/口播词.md (12段), 台本/分镜.md (12个 shot), 台本/视频提示词.json
  state.json: phase=write

用户: /video-review
  ↓
  Claude 读 设定+台本+提示词，输出 review.md
  标出: "S07 口播词'注意力机制'与 S06 解释有逻辑断裂"

用户: /video-visual
  ↓
  Claude 读 视频提示词.json:
    - 缺: 小明_白大褂四视图 → CLI four-views
    - 缺: 实验室_master → CLI scene-master
    - 缺: 12 个 shot 视频 → CLI video-generate (12 次 Seedance)
  state.json: phase=visual
  assets.json 记录所有资产

用户: /video-finish
  ↓
  Claude 读 口播词.md, 素材/视频/S01..S12.mp4:
    - 解析口播词为时间轴 → 字幕.srt
    - ffmpeg 拼接 12 个 mp4 → 终版_raw.mp4
    - ffmpeg 烧字幕 → 终版_subtitled.mp4
    - ffmpeg 叠加 BGM (来自 plugin/assets/bgm/) → 终版_final.mp4
    - 封面: Seedance 生成 1 张 16:9 + 裁 9:16 → 封面.png
    - 发布/: 标题与描述.txt, 标签.json, 发布清单.md
  state.json: phase=done
```

---

## 6. 设计决策日志

| # | 决策 | 原因 |
|---|---|---|
| 1 | 与 short-drama-writer 关系：**独立插件 + 共享后端** | 后端重写成本高，AI 能力（火山引擎）已就绪；新插件专注创作侧差异化 |
| 2 | 内容类型：通用骨架（适配各类） | 用户原话"用于各类短视频的制作"，不绑死内容 |
| 3 | 范围：先做概念设计，不锁 MVP | 用户原话"概念设计先，不定 MVP" |
| 4 | 独特能力：4 个全要（语音/发行/选题/多项目管理） | 用户明确"都加上" |
| 5 | 项目单位：单视频 = 一个项目 | 简单直接，符合用户心智 |
| 6 | 多项目管理：暂不实现（YAGNI） | 用户明确"不做了"。多项目粒度由用户用 OS 文件管理器解决 |
| 7 | query / dashboard skill：都不做 | 单视频场景下信息量小，Claude 直接读文件即可 |
| 8 | 后端边界：在短剧后端加新模块（实际只需加 2-3 个 CLI） | 用户原话"后端加服务模块"。经审视后实际改动极小 |
| 9 | 平台发行深度：仅生成本地变体（文件 + 元数据） | 用户明确不要调平台 API。规避账号/OAuth 复杂度 |
| 10 | 变体生成（多比例裁剪）：不做 | 用户原话"B，但是变体生成可以不需要" |
| 11 | 纯旁白型：Seedance 自带，不接 TTS | 用户指出 Seedance 已支持 |
| 12 | 视频生成拆为 visual + finish 两阶段 | visual = AI 生成片段，finish = ffmpeg 拼装。这是 Seedance 5-10s 限制的必然 |
| 13 | voice provider / TTS / music provider：不接 | Seedance 2.0 已带音频生成 + 口型同步。短剧后端基础设施复用 |
| 14 | 字幕：纯本地文本处理 | 不算"生成"，是脚本 → srt 格式化 + ffmpeg 烧录 |
| 15 | 状态机保护：phase=done 可重跑，其他按序 | 与短剧 state.json 模式一致 |

---

## 7. 错误处理

### 7.1 失败模式与对策

| 失败点 | 触发 | 对策 |
|---|---|---|
| Seedance content filter | 提示词命中敏感词 | 重试一次（换同义词）；再失败则把该 shot 标记为 `failed` 跳过，继续后续 shot |
| Seedance 提交失败 (401/403) | API key 失效 | 立即终止，提示用户检查 `.env` 配置 |
| Seedance 提交失败 (429) | 限流 | CLI 已有 `submit_lock` 串行化；本插件保留 |
| Seedance 轮询超时 (>30 分钟) | 服务端卡死 | 标记 shot 为 `timeout`，跳过，继续后续 |
| TOS 上传失败 | 网络断 | 本地保留图片字节但不上传；标记 `tos_url=""`，下游生成视频时缺 reference |
| ffmpeg 失败 | 字幕 srt 损坏、mp4 codec 不兼容 | 终止 finish，列出哪个步骤失败、错误输出 |
| 角色/场景资产缺失 | 用户跳过了 visual 阶段某些资产 | 视频生成时该 shot 标记 `incomplete_assets`，产物可能与预期不符，发布前提示 |

### 7.2 重试与幂等

- **重试粒度**：单 shot 级别。失败 1 个 shot 不影响其他 9 个。
- **幂等保护**：`assets.json` 是唯一真相。再调一次 visual，已存在的资产跳过、不重发 API。
- **断点续跑**：用户 `/video-visual` 跑一半中断，重跑时已完成的 shot 跳过。

### 7.3 用户可见的错误呈现

不静默吞错。每个 CLI 调用捕获异常 → 写一行 human-readable 错误到 stderr → 继续/终止。`/video-review` 在 review.md 里也加一节"已知问题清单"（来自上轮 visual 的失败记录）。

---

## 8. 测试策略

### 8.1 测试金字塔

```
           ╱  ╲
          ╱ 端到端  ╲         ← 手动跑：test-project fixture
         ╱──────────╲
        ╱  集成测试   ╲        ← pytest：plugin/scripts/ 调 mock 后端
       ╱──────────────╲
      ╱   单元测试       ╲     ← pytest：state machine / JSON schema / 路径解析
     ╱────────────────────╲
```

### 8.2 各层测试内容

| 层 | 内容 | 工具 |
|---|---|---|
| **单元** | state.json 状态机转移合法性、视频提示词 JSON schema 校验、assets.json 读写、字幕时间轴生成纯函数、发布元数据序列化 | pytest |
| **集成** | plugin/scripts/ 调 mock 后端：mock `jimeng.generate`、`seedance.generate` 返回 fixture 文件；验证 CLI 命令产物路径、assets.json 写入正确 | pytest + monkeypatch |
| **端到端** | 一个 test-project fixture 走完 5 个 skill。手动跑或半自动（API 调用真后端，需 token） | 手动 + 录屏 |

### 8.3 不能/不应测的部分

- **Seedance 真实生成**：贵、慢、不确定。生产跑过即可。
- **Claude 创意决策**（写台本、review 反馈）：质量主观，只能人工 spot check。
- **ffmpeg 跨平台兼容性**：在 CI 跑基本功能即可（macOS / Linux / Windows 三平台各跑一次 smoke）。

### 8.4 测试目录结构

```
short-video-studio/
├── tests/
│   ├── unit/
│   │   ├── test_state_machine.py
│   │   ├── test_video_prompt_schema.py
│   │   ├── test_subtitle_srt.py
│   │   └── test_publish_metadata.py
│   ├── integration/
│   │   ├── test_visual_skill.py      # mock jimeng/seedance
│   │   └── test_finish_skill.py      # mock ffmpeg / use real ffmpeg
│   ├── fixtures/
│   │   ├── mock_jimeng_4views.png
│   │   ├── mock_seedance_clip.mp4
│   │   └── test_video_prompt.json
│   └── conftest.py
├── pytest.ini
└── requirements-dev.txt
```

### 8.5 CI 策略

- 跑 unit + integration（mock 后端） on PR
- 端到端手动跑（带 Seedance token） before release
- 三个 OS 各跑一次 ffmpeg smoke

---

## 9. 后续（MVP 切片待定）

本设计文档为概念设计层。具体 MVP 切片、release 节奏、任务拆分留待 writing-plans 阶段。

待 MVP 阶段决定：
- 哪些 skill 先实现（如最小可演示路径 = init + write + visual + finish，跳过 review）
- 类型模板首批支持哪几类（知识科普？营销种草？）
- 后端 video-cover CLI 是否在 MVP 范围
- 测试是否进 MVP

---

## 10. 附录

### 10.1 术语对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 短视频 | short video | 单条独立视频，15-90s |
| 短剧 | short drama | 多集连续剧，1-3min × 10+ 集 |
| 钩子 | hook | 视频前 3 秒抓住注意力的设计 |
| 口播词 | narration script | 视频中讲述的完整文字 |
| 分镜 | storyboard | 镜头列表 + 描述 |
| 取景框 | shot frame | 镜头对应的取景构图 |
| 四视图 | four-views | 角色前/侧/背/特写的 4 个角度 |
| 终版 | final cut | 完整成片 |

### 10.2 关联项目

- `D:\PersonalFiles\Project_Space\short-drama-writer` — 复用后端与其插件模式
