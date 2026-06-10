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
读 `<PROJECT>/设定/角色.md` 拿到角色锚点（不可变）和可变项。
读 `<PROJECT>/设定/场景.md` 拿到场景空间描述、光线色调、氛围基调。
读 `<PROJECT>/设定/视觉风格.md` 拿到整体风格。

### 步骤 2：生成 <PROJECT>/台本/口播词.md

**台本质量直接决定完播率。** 按所选类型模板的脚本结构写作，遵守以下铁律：

**开头（最关键）**：
- 第一句 ≤ 12 个字，直接进冲突/悬念/场景
- 禁止"大家好我是XXX"、"今天我们来聊聊"
- 0.5 秒内制造认知缺口（不看完不舒服）

**中段**：
- 每 3-5 秒有新信息（新画面/新文案/新音效交替）
- 禁止"第一点/第二点/第三点"清单体
- 知识科普用 SCQA（情境→冲突→疑问→解答）
- 数字代替形容词："3个雷区" > "重要提醒"
- 情绪用身体细节描述，不用抽象形容词

**结尾（最后 5 秒，干脆利落）**：
- 金句收尾 / 开放问题引导评论 / 可验证的落地方法
- 禁止"关注我点赞收藏"模板引导（算法已降权）
- 故事型留白不总结，科普型回归开头钩子

**格式**：每段带时间轴，段长 3-7s。

```markdown
# <视频主题> — 口播词

## 总时长：<duration> 秒

[00:00.000 → 00:03.500]
<钩子完整文字，≤12字起手>

[00:03.500 → 00:08.000]
<第一段内容>

...

[01:25.000 → 01:30.000]
<结尾：金句/开放问题/可验证方法>
```

时间轴精度 0.5s。Subtitle 解析器会读这个。

### 步骤 3：生成 <PROJECT>/台本/分镜.md

每个 shot 一行，参考 设定/场景.md 的机位方向：

```markdown
# 分镜

| shot_id | 时长 | 场景 | 角色 | 机位 | 动作 |
|---|---|---|---|---|---|
| S01 | 3.5s | 实验室 | 小明 | 中景 | 面对镜头微微点头 |
| S02 | 4.5s | 实验室 | 小明 | 近景 | 拿起试管观察 |
| S03 | 5.0s | 实验室 | 小明 | 特写 | 手指轻点桌面 |
...
```

总时长应与口播词的总时长一致。

### 步骤 4：分镜合并为生成段

Seedance 2.0 在同一 prompt 中用 `镜头1`、`镜头2` 标记多个连续镜头，模型自己处理转场——比 ffmpeg 硬拼接流畅。

**合并规则**：
- 同一场景 + 连续时间 → 合并为一个生成段
- 累加时长 ≤ 15 秒（Seedance 单次上限）
- 场景切换 / 时间跳跃 / 角色变化 → 拆分为新段

在分镜表上标注段号：

```markdown
# 分镜

| shot_id | 时长 | 场景 | 角色 | 机位 | 动作 | 段 |
|---|---|---|---|---|---|---|
| S01 | 3.5s | 实验室 | 小明 | 中景 | 面对镜头微微点头 | seg1 |
| S02 | 4.5s | 实验室 | 小明 | 近景 | 拿起试管观察        | seg1 |
| S03 | 5.0s | 实验室 | 小明 | 特写 | 手指轻点桌面        | seg1 |
| S04 | 4.0s | 走廊   | 小明 | 全景 | 快步走出实验室      | seg2 |
| S05 | 5.0s | 走廊   | 小明 | 中景 | 与同事交谈          | seg2 |
...
```

> seg1 三个镜头同场景，总时长 13s ≤ 15s → 一个 prompt 生成。seg2 场景变了，拆开。

### 步骤 5：生成 <PROJECT>/台本/视频提示词.json

**prompt 字段使用 Seedance 2.0 官方公式**：

```
精准主体 + 动作细节 + 场景环境 + 光影色调 + 镜头运镜 + 视觉风格 + 画质 + 约束条件
```

**段内合并**：同一个 segment 的多个 shot，在一个 prompt 中用 `镜头1`、`镜头2`... 串联，Seedance 自己处理镜头间转场。场景切换处自然分段。
每个 shot 记录自己的 `segment_id` 和 `narration`，同段 shot 共享一个合并的 `prompt`。

**锚点锁定规则**：从 `<PROJECT>/设定/角色.md` 取每个角色的锚点词（发型发色、脸型特征、标志配饰、体型身高、着装基底），**在全部 shot 的 prompt 中一字不改原样粘贴**。

**动作描述规则**（官方要求）：
- 肢体细化 + 程度量化：缓慢抬手、微微低头、手指轻敲桌面
- 情绪外化：不说"很紧张"，说"频繁看手表、呼吸急促"
- 优先低缓连贯小动作，规避狂奔大跳剧烈翻滚

**符号规范**：音效 `<>`、台词 `{}`、字幕 `【】`

**官方约束词（每个 prompt 末尾必加）**：`保持无字幕，不要生成Logo，不要生成水印`

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
            "segment_id": "seg1",
            "order": 1,
            "scene": "实验室",
            "frame_type": "establishing",
            "narration": "<从口播词对应段复制>",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": (
                "镜头1：中景，缓慢推镜，黑色短发偏分方脸浓眉银领针的男研究员穿着白大褂深灰衬衫，"
                "面对镜头微微点头，双手自然放在实验台上。"
                "镜头2：近景，轻微推入，黑色短发偏分方脸浓眉银领针的男研究员穿着白大褂深灰衬衫，"
                "右手拿起试管对着灯光观察，表情专注。"
                "镜头3：特写，固定镜头，手指轻点桌面，试管放在一旁。"
                "实验室背景，柔和晨窗光，半写实CG渲染，低饱和清新色调。"
                "高清电影质感，保持无字幕，不要生成Logo，不要生成水印。"
            ),
            "video_params": {
                "duration_sec": 13,
                "aspect_ratio": "9:16"
            }
        },
        {
            "shot_id": "S02",
            "segment_id": "seg1",
            "order": 2,
            "scene": "实验室",
            "frame_type": "close_up",
            "narration": "<口播词下一段>",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": "",  # 同段复用 seg1 的 prompt，此处留空
            "video_params": {
                "duration_sec": 0,
                "aspect_ratio": "9:16"
            }
        },
        {
            "shot_id": "S03",
            "segment_id": "seg1",
            "order": 3,
            "scene": "实验室",
            "frame_type": "close_up",
            "narration": "<口播词下一段>",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": "",
            "video_params": {
                "duration_sec": 0,
                "aspect_ratio": "9:16"
            }
        },
        {
            "shot_id": "S04",
            "segment_id": "seg2",
            "order": 4,
            "scene": "走廊",
            "frame_type": "establishing",
            "narration": "<口播词下一段>",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": (
                "镜头1：全景，平稳横移，黑色短发偏分方脸浓眉银领针的男研究员穿着白大褂深灰衬衫，"
                "快步走出实验室进入走廊。"
                "镜头2：中景，固定镜头，与走廊里的同事停下交谈，表情认真。"
                "走廊白墙日光灯，写实风格，微冷色调。"
                "高清电影质感，保持无字幕，不要生成Logo，不要生成水印。"
            ),
            "video_params": {
                "duration_sec": 9,
                "aspect_ratio": "9:16"
            }
        },
        {
            "shot_id": "S05",
            "segment_id": "seg2",
            "order": 5,
            "scene": "走廊",
            "frame_type": "medium",
            "narration": "<口播词下一段>",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": "",
            "video_params": {
                "duration_sec": 0,
                "aspect_ratio": "9:16"
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

> **段结构说明**：`segment_id` 相同的 shot 属于同一生成段。每段第一个 shot 的 `prompt` 包含完整的 `镜头1/镜头2...` 串联描述、场景、风格、约束词；同段后续 shot 的 `prompt` 留空。`video_params.duration_sec` 为**整段**总时长（≤ 15s），非首 shot 填 0。

### 步骤 6：更新 state

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

- **锚点锁定**：角色锚点词从 设定/角色.md 原样复制到每个 shot prompt，一字不改
- **官方公式**：精准主体 + 动作细节 + 场景环境 + 光影色调 + 镜头运镜 + 视觉风格 + 画质 + 约束条件
- **一镜一动**：每个镜头只一种运镜方式，不推拉摇移混合
- **分镜用镜头序号**：`镜头1`、`镜头2`，不写精确时间戳
- **官方约束词**：每个 prompt 末尾加 `保持无字幕，不要生成Logo，不要生成水印`
- **符号规范**：音效 `<>`、台词 `{}`、字幕 `【】`
- **动作低缓化**：优先细微连贯动作，情绪用身体细节表达
- 提示词应包含 视觉风格.md 中的风格关键词
- 场景引用应与 设定/场景.md 一致
- 视频总时长应与 设定/视频档案.md 一致
- 必须在写完文件后调用 `validate_video_prompt` 校验
