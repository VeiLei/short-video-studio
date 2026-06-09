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
