from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KeysConfig:
    """Keyboard binding configuration for Aperture."""
    # Navigation
    scroll_down: str = "j"
    scroll_up: str = "k"
    jump_to_top: str = "g"
    jump_to_bottom: str = "G"
    # Search
    search: str = "slash"
    next_match: str = "n"
    prev_match: str = "N"
    # Panes
    open_pane: str = "p"
    horizontal_split: str = "h"
    vertical_split: str = "v"
    floating_split: str = "f"
    # General
    mouse_toggle: str = "m"
    help: str = "?"
    quit: str = "q"
