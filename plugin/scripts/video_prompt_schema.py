"""视频提示词 JSON schema 校验。

定义 spec §5.1 的结构，校验台本输出合法性。
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

VALID_TYPES = {"knowledge", "marketing", "story", "vlog", "news", "other"}
VALID_PLATFORMS = {"douyin", "kuaishou", "xiaohongshu", "bilibili", "shipinhao", "other"}
VALID_FRAME_TYPES = {"establishing", "two_shot", "close_up", "over_shoulder", "insert", "other"}


class ValidationError(Exception):
    """视频提示词不符合 schema。"""


SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["video_id", "title", "type", "target_platform", "aspect_ratio", "shots"],
    "properties": {
        "video_id": {"type": "string"},
        "title": {"type": "string"},
        "type": {"type": "string", "enum": list(VALID_TYPES)},
        "target_platform": {"type": "string", "enum": list(VALID_PLATFORMS)},
        "aspect_ratio": {"type": "string", "pattern": r"^\d+:\d+$"},
        "total_duration_sec": {"type": "integer", "minimum": 1},
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["shot_id", "order", "prompt", "video_params"],
                "properties": {
                    "shot_id": {"type": "string"},
                    "order": {"type": "integer", "minimum": 1},
                    "scene": {"type": "string"},
                    "frame_type": {"type": "string", "enum": list(VALID_FRAME_TYPES)},
                    "narration": {"type": "string"},
                    "dialogue": {"type": "string"},
                    "characters": {"type": "array", "items": {"type": "string"}},
                    "outfits": {"type": "array", "items": {"type": "string"}},
                    "prompt": {"type": "string", "minLength": 1},
                    "video_params": {
                        "type": "object",
                        "required": ["duration_sec"],
                        "properties": {
                            "duration_sec": {"type": "integer", "minimum": 1},
                            "aspect_ratio": {"type": "string", "pattern": r"^\d+:\d+$"},
                            "camera": {"type": "string"},
                            "motion": {"type": "string"},
                        },
                    },
                },
            },
        },
    },
}


def validate_video_prompt(data: dict[str, Any]) -> None:
    """校验视频提示词 JSON。

    Raises:
        ValidationError: 不符合 schema 时。
    """
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        raise ValidationError("jsonschema package not installed. Run: pip install jsonschema")

    validator = Draft7Validator(SCHEMA)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    for err in errors:
        path = ".".join(str(p) for p in err.path) or "<root>"
        raise ValidationError(f"{path}: {err.message}")

    # Soft warning for long durations
    for shot in data.get("shots", []):
        dur = shot.get("video_params", {}).get("duration_sec", 0)
        if dur > 30:
            logger.warning(
                "Shot %s duration_sec=%d exceeds Seedance 30s limit; will be split.",
                shot.get("shot_id", "?"), dur,
            )
