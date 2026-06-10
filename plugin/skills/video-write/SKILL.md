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

- 当前工作目录是项目根目录（即包含 `.video/state.json` 的目录）
- `设定/` 目录含 视频档案.md、角色.md、场景.md、视觉风格.md

**项目目录确认**：读取 `.video/state.json` 获取 `video_id`，当前目录即为 `PROJECT`。
所有读取和写入都相对于 `PROJECT/`。

## 工作流

### 步骤 1：确认项目目录并读 设定/

先用 `Read` 读 `.video/state.json` 确认当前目录是项目根目录，获取 `video_id`。

读 `<PROJECT>/设定/视频档案.md` 拿到主题、类型、平台、时长、钩子策略、推荐结构。
读 `<PROJECT>/设定/角色.md` 拿到角色外观/动作。
读 `<PROJECT>/设定/场景.md` 拿到场景信息。
读 `<PROJECT>/设定/视觉风格.md` 拿到整体风格。

### 步骤 2：生成 <PROJECT>/台本/口播词.md

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

...

[01:25.000 → 01:30.000]
<CTA 文字>
```

时间轴精度 0.5s，段长 3-7s。Subtitle 解析器会读这个。

### 步骤 3：生成 <PROJECT>/台本/分镜.md

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

### 步骤 4：生成 <PROJECT>/台本/视频提示词.json

**注意**：`<PROJECT>` 是项目根目录的绝对路径（即包含 `.video/state.json` 的目录）。

**prompt 字段必须使用五层填空式结构**（Seedance 2.0 验证最佳实践）：

```
主体: [角色锚点词原样复制] + [着装]
动作: [一个动词短语，现在时]
镜头: [景别] + [运动] + [角度]，[焦距感受]
风格: [视觉风格锚点]，[布光]，[色调]
约束: [排除项]，稳定约束词
```

**锚点锁定规则**：从 `<PROJECT>/设定/角色.md` 取每个角色的锚点词，**在全部 shot 的 prompt 中一字不改原样粘贴**。只换动作、镜头、风格三行。

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("d:/PersonalFiles/Project_Space/short-video-studio/plugin/scripts").resolve()))
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
            "prompt": (
                "主体: 黑色短发齐刘海，圆脸左颊小痣，细框眼镜，金圈耳环，白大褂浅蓝衬衫，中等身材。"
                "动作: 面对镜头微微点头，双手自然放在实验台上。"
                "镜头: 中景，缓慢推入，眼平高度，35mm感。"
                "风格: 柔和晨窗光，低饱和色调，半写实CG渲染，知识科普质感。"
                "约束: 无跳跃变焦，无额外角色，保持角色特征一致，画面连贯流畅。"
            ),
            "video_params": {
                "duration_sec": 6,
                "aspect_ratio": "9:16",
                "camera": "中景",
                "motion": "缓慢推入"
            }
        },
        {
            "shot_id": "S02",
            "order": 2,
            "scene": "实验室",
            "frame_type": "close_up",
            "narration": "<口播词下一段>",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": (
                "主体: 黑色短发齐刘海，圆脸左颊小痣，细框眼镜，金圈耳环，白大褂浅蓝衬衫，中等身材。"
                "动作: 右手拿起试管对着灯光观察，表情专注。"
                "镜头: 近景特写，轻微推入，略高于眼平，85mm感。"
                "风格: 柔和晨窗光，低饱和色调，半写实CG渲染，知识科普质感。"
                "约束: 无跳跃变焦，无额外角色，保持角色特征一致，画面连贯流畅。"
            ),
            "video_params": {
                "duration_sec": 5,
                "aspect_ratio": "9:16",
                "camera": "近景",
                "motion": "轻微推入"
            }
        }
    ]
}

validate_video_prompt(data)

Path("<PROJECT>/台本/视频提示词.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
```

> **五层结构要点**：主体行全镜头原样锁定；动作行每镜头只一个动词；镜头行指定景别+运动+焦距感；风格行固定布光和色调；约束行包含排除项+稳定约束词。短 prompt 比长文效果好，控制在 60 词以内。

### 步骤 5：更新 state

```bash
cd d:/PersonalFiles/Project_Space/short-video-studio
.venv/Scripts/python -c "
import sys
sys.path.insert(0, 'plugin/scripts')
from state_manager import StateManager
StateManager('<PROJECT>').set_phase('write')
"
```

## 关键约束

- **锚点锁定**：角色锚点词从 设定/角色.md 原样复制到每个 shot prompt 的主体行，一字不改
- **五层结构**：每个 shot prompt 严格按 主体→动作→镜头→风格→约束 结构，控制 60 词以内
- **一镜一动**：每个镜头只一个运动动词，复合运动拆成多个 shot
- **稳定约束词**：每个 prompt 末尾加"保持角色特征一致，画面连贯流畅"
- **排除项**：每镜头选 3-5 个排除项（如"无跳跃变焦、无额外角色、无文字叠加"）
- 提示词应包含 视觉风格.md 中的关键词
- 场景引用应与 设定/场景.md 一致
- 视频总时长应与 设定/视频档案.md 一致
- 必须在写完文件后调用 `validate_video_prompt` 校验
