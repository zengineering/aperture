from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from toolong.config.schema import (
    ApertureConfig,
    KeysConfig,
    PanesConfig,
    ThemeConfig,
    VALID_SPLITS,
)

_CONFIG_PATH = Path.home() / ".config" / "aperture" / "config.toml"
_DEFAULTS_PATH = Path(__file__).parent / "defaults.toml"

# Maps hyphenated TOML key names to Python field names on KeysConfig.
_KEYS_MAP: Dict[str, str] = {
    "scroll-down": "scroll_down",
    "scroll-up": "scroll_up",
    "jump-to-top": "jump_to_top",
    "jump-to-bottom": "jump_to_bottom",
    "next-match": "next_match",
    "prev-match": "prev_match",
    "open-pane": "open_pane",
    "horizontal-split": "horizontal_split",
    "vertical-split": "vertical_split",
    "floating-split": "floating_split",
    "mouse-toggle": "mouse_toggle",
}

T = TypeVar("T")


def _from_raw(cls: Type[T], raw: Dict[str, Any]) -> T:
    """Instantiate a dataclass from a raw dict, ignoring unknown keys."""
    valid = {f.name for f in fields(cls)}  # type: ignore[arg-type]
    return cls(**{k: v for k, v in raw.items() if k in valid})


def load_config(config_path: Path | None = None) -> ApertureConfig:
    """Load config from path, creating it from bundled defaults on first run."""
    path = config_path if config_path is not None else _CONFIG_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_DEFAULTS_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    with open(path, "rb") as f:
        raw: Dict[str, Any] = tomllib.load(f)
    return _build_config(raw)


def _build_config(raw: Dict[str, Any]) -> ApertureConfig:
    theme = _from_raw(ThemeConfig, raw.get("theme", {}))
    keys_raw = {_KEYS_MAP.get(k, k): v for k, v in raw.get("keys", {}).items()}
    keys = _from_raw(KeysConfig, keys_raw)
    panes_raw = raw.get("panes", {})
    split = panes_raw.get("default-split", "horizontal")
    if split not in VALID_SPLITS:
        raise ValueError(
            f"Invalid panes.default-split {split!r}. Must be one of: "
            + ", ".join(sorted(VALID_SPLITS))
        )
    panes = PanesConfig(default_split=split)
    return ApertureConfig(theme=theme, keys=keys, panes=panes)
