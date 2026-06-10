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

- 用户当前在项目父目录（例如 `mkdir 我的视频 && cd 我的视频`，在此目录下启动 Claude Code）
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

### 步骤 2：调用 init_project 创建项目目录

`video_id` 格式：`v_YYYY-MM-DD_NNN`，如 `v_2026-06-09_001`。

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

**记下输出的绝对路径，设为 `PROJECT`。后续所有文件写入都必须在 `PROJECT/` 下。**

例如输出 `D:\xxx\我的视频\v_2026-06-09_001`，则：
- `设定/` → `D:\xxx\我的视频\v_2026-06-09_001\设定\`
- `台本/` → `D:\xxx\我的视频\v_2026-06-09_001\台本\`

### 步骤 3：套用类型模板生成 设定/视频档案.md

读取 `plugin/templates/types/<type>.md`，写入 `<PROJECT>/设定/视频档案.md`：

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

### 步骤 4：生成 <PROJECT>/设定/角色.md（如果出镜）

**角色锚点系统**：每个出镜角色必须定义 3-7 个不可变锚点特征。这些锚点词在 `video-write` 生成每个 shot prompt 时原样锁定不变，以确保 Seedance 多镜头角色一致性。

```markdown
# 角色

## <角色名>

- **身份**：<身份，如"白大褂研究员"、"咖啡摊主">

### 角色锚点（不可变，每个镜头原样复制）
- **发型/发色**：<如"黑色短发、齐刘海">
- **脸型特征**：<如"圆脸、左颊小痣、细框眼镜">
- **标志配饰**：<如"金圈耳环、银色手表">
- **体型/身高**：<如"中等身材、170cm左右">
- **着装基底**：<如"白大褂+浅蓝衬衫">

### 可变项（按场景切换）
- **穿搭变体**：<基础着装 / 正装 / 休闲>
- **表情/情绪**：<平静讲述 / 惊讶 / 微笑>

- **口播风格**：<语气、节奏>
- **典型动作**：<3-5 个常用动作>
```

> **锚点原则**：锚点词必须简短具体，每个 shot 提示词中一字不改地粘贴。避免抽象描述（"好看的"），用可度量细节（"左颊小痣"、"金圈耳环"）。

### 步骤 5：生成 <PROJECT>/设定/场景.md

```markdown
# 场景

## <场景名>

- **空间描述**：<室内/室外、布局>
- **关键地标**：<3-5 个标志性物品>
- **光线/色调**：<冷暖、光源方向>
- **氛围基调**：<专注/轻松/紧张>
```

### 步骤 6：生成 <PROJECT>/设定/视觉风格.md

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

- **所有生成的文件必须写入 PROJECT 目录内**，不能写到当前工作目录
- 不要在项目目录创建 .py 脚本，始终用 `plugin/scripts/` 里的模块
- type 字段必须是白名单中的一个（参考 `video_prompt_schema.py`）
- aspect_ratio 默认 9:16（除非用户明确要其他比例）
- 不要生成大纲/分集/章节（短视频没有这些概念）
