"""测试口播词 → SRT 字幕生成。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from subtitle_gen import parse_narration_to_srt, write_srt


NARRATION = """# 我的视频

[00:00.000 → 00:03.500]
你有没有想过，ChatGPT 是怎么理解人话的？

[00:03.500 → 00:07.200]
今天我们用 3 分钟讲清楚 Transformer。

[00:07.200 → 00:12.000]
先从一个简单的问题开始。
"""


def test_parse_extracts_cues():
    """parse_narration_to_srt 应从 markdown 提取时间轴条目。"""
    cues = parse_narration_to_srt(NARRATION)
    assert len(cues) == 3
    assert cues[0]["start_ms"] == 0
    assert cues[0]["end_ms"] == 3500
    assert "你有没有想过" in cues[0]["text"]


def test_srt_format():
    """SRT 格式：序号 + 时间 + 文本 + 空行。"""
    cues = parse_narration_to_srt(NARRATION)
    srt = write_srt(cues)
    assert "1\n" in srt
    assert "00:00:00,000 --> 00:00:03,500" in srt
    assert "你有没有想过" in srt
    assert "\n\n2\n" in srt  # 条目间空行


def test_srt_writes_to_file(tmp_path):
    """write_srt 接受 path 参数。"""
    cues = parse_narration_to_srt(NARRATION)
    out = tmp_path / "out.srt"
    write_srt(cues, path=str(out))
    content = out.read_text(encoding="utf-8")
    assert "00:00:00,000" in content


def test_empty_narration_returns_empty():
    """无时间轴标记的纯文本返回空列表。"""
    cues = parse_narration_to_srt("就是一些普通文本")
    assert cues == []
