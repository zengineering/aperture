from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


VALID_SPLITS = {"horizontal", "vertical", "floating"}


@dataclass
class ThemeConfig:
    accent: Optional[str] = None
    background: Optional[str] = None
    foreground: Optional[str] = None
    panel_background: Optional[str] = None
    panel_foreground: Optional[str] = None
    border: Optional[str] = None
    primary: Optional[str] = None
    secondary: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None
    success: Optional[str] = None
    info: Optional[str] = None


@dataclass
class KeysConfig:
    scroll_down: str = "j"
    scroll_up: str = "k"
    jump_to_top: str = "g"
    jump_to_bottom: str = "G"
    search: str = "/"
    next_match: str = "n"
    prev_match: str = "N"
    open_pane: str = "enter"
    horizontal_split: str = "s"
    vertical_split: str = "v"
    floating_split: str = "f"
    mouse_toggle: str = "m"
    help: str = "?"
    quit: str = "q"


@dataclass
class PanesConfig:
    default_split: str = "horizontal"


@dataclass
class ApertureConfig:
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    keys: KeysConfig = field(default_factory=KeysConfig)
    panes: PanesConfig = field(default_factory=PanesConfig)
