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
