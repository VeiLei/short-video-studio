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
