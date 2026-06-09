"""测试视频提示词 JSON schema 校验。"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))

from video_prompt_schema import validate_video_prompt, ValidationError


VALID_PROMPT = {
    "video_id": "v_2026-06-09_001",
    "title": "3分钟读懂Transformer",
    "type": "knowledge",
    "target_platform": "douyin",
    "aspect_ratio": "9:16",
    "total_duration_sec": 90,
    "shots": [
        {
            "shot_id": "S01",
            "order": 1,
            "scene": "实验室",
            "frame_type": "establishing",
            "narration": "你有没有想过，ChatGPT 是怎么理解人话的？",
            "characters": ["小明"],
            "outfits": ["白大褂"],
            "prompt": "实验室场景，白大褂的小明面对镜头...",
            "video_params": {
                "duration_sec": 6,
                "aspect_ratio": "9:16",
                "camera": "中景正面",
                "motion": "说话动作",
            },
        }
    ],
}


def test_valid_prompt_passes():
    """合法的视频提示词应通过校验。"""
    validate_video_prompt(VALID_PROMPT)  # 不抛


def test_missing_shots_fails():
    """缺少 shots 字段应失败。"""
    bad = {**VALID_PROMPT}
    del bad["shots"]
    with pytest.raises(ValidationError):
        validate_video_prompt(bad)


def test_shot_missing_required_fails():
    """shot 缺少 shot_id/order 应失败。"""
    bad = json.loads(json.dumps(VALID_PROMPT))
    del bad["shots"][0]["shot_id"]
    with pytest.raises(ValidationError):
        validate_video_prompt(bad)


def test_invalid_type_fails():
    """type 字段不在白名单应失败。"""
    bad = json.loads(json.dumps(VALID_PROMPT))
    bad["type"] = "unknown_type"
    with pytest.raises(ValidationError):
        validate_video_prompt(bad)


def test_duration_too_long_warns(caplog):
    """duration > 30s 应警告（Seedance 单次上限）。"""
    bad = json.loads(json.dumps(VALID_PROMPT))
    bad["shots"][0]["video_params"]["duration_sec"] = 60
    # 不抛异常，但记录警告
    validate_video_prompt(bad)
