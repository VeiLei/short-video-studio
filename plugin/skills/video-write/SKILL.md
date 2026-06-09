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
