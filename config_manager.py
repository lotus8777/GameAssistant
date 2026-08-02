"""配置持久化管理。"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


CONFIG_PATH = _app_dir() / "config.json"


@dataclass
class KeyAction:
    """单个按键动作配置。"""

    key: str = "1"
    interval_ms: int = 1000
    cast_time_ms: int = 100
    enabled: bool = True
    repeat_count: int = 0  # 0 表示无限循环

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KeyAction":
        return cls(
            key=str(data.get("key", "1")),
            interval_ms=int(data.get("interval_ms", 1000)),
            cast_time_ms=int(data.get("cast_time_ms", 100)),
            enabled=bool(data.get("enabled", True)),
            repeat_count=int(data.get("repeat_count", 0)),
        )


@dataclass
class AppConfig:
    """应用全局配置。"""

    toggle_hotkey: str = "f6"
    actions: list[KeyAction] = field(default_factory=list)

    @classmethod
    def default(cls) -> "AppConfig":
        return cls(
            toggle_hotkey="f6",
            actions=[
                KeyAction(key="1", interval_ms=1000),
                KeyAction(key="2", interval_ms=1500),
            ],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        actions = [KeyAction.from_dict(item) for item in data.get("actions", [])]
        return cls(
            toggle_hotkey=str(data.get("toggle_hotkey", "f6")),
            actions=actions or cls.default().actions,
        )


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        config = AppConfig.default()
        save_config(config)
        return config

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return AppConfig.from_dict(data)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return AppConfig.default()


def save_config(config: AppConfig) -> None:
    payload = {
        "toggle_hotkey": config.toggle_hotkey,
        "actions": [asdict(action) for action in config.actions],
    }
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
