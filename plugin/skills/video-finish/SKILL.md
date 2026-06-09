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
