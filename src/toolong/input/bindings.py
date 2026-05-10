from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from textual.binding import Binding
from textual.keys import KEY_NAME_REPLACEMENTS

# Navigation
KEY_SCROLL_DOWN    = "j"
KEY_SCROLL_UP      = "k"
KEY_JUMP_TO_TOP    = "g"
KEY_JUMP_TO_BOTTOM = "G"

BIND_SCROLL_DOWN    = Binding(KEY_SCROLL_DOWN,    "scroll_down", show=False)
BIND_SCROLL_UP      = Binding(KEY_SCROLL_UP,      "scroll_up",   show=False)
BIND_JUMP_TO_TOP    = Binding(KEY_JUMP_TO_TOP,    "scroll_home", show=False)
BIND_JUMP_TO_BOTTOM = Binding(KEY_JUMP_TO_BOTTOM, "scroll_end",  show=False)

# Search
KEY_SEARCH     = "slash"
KEY_NEXT_MATCH = "n"
KEY_PREV_MATCH = "N"

BIND_SEARCH     = Binding(KEY_SEARCH,     "show_find_dialog", "Find", key_display="/")
BIND_NEXT_MATCH = Binding(KEY_NEXT_MATCH, "next_match",       show=False)
BIND_PREV_MATCH = Binding(KEY_PREV_MATCH, "prev_match",       show=False)

# General
KEY_MOUSE_TOGGLE = "m"
KEY_HELP         = "?"
KEY_QUIT         = "q"

BIND_MOUSE_TOGGLE = Binding(KEY_MOUSE_TOGGLE, "toggle_mouse", "Mouse", show=False)
BIND_HELP         = Binding(KEY_HELP,         "help",         "Help")
BIND_QUIT         = Binding(KEY_QUIT,         "quit",         "Quit")


def normalize_key(key: str) -> str:
    """Normalize a single-character key to the name Textual expects in bindings.

    Replicates the logic of textual.keys._character_to_key using only public
    APIs (KEY_NAME_REPLACEMENTS and unicodedata).
    """
    if len(key) != 1:
        return key
    if not key.isalnum():
        try:
            name = unicodedata.name(key).lower().replace("-", "_").replace(" ", "_")
        except ValueError:
            raise ValueError(
                f"{key!r} is not a valid bindable character. "
                f"Check your ~/.config/aperture/config.toml."
            )
    else:
        name = key
    return KEY_NAME_REPLACEMENTS.get(name, name)


@dataclass(frozen=True)
class BindingEntry:
    """Maps a human-readable label to a KeysConfig field name."""
    label: str
    field: str

    def __post_init__(self) -> None:
        import dataclasses
        from toolong.config.schema import KeysConfig
        valid = {f.name for f in dataclasses.fields(KeysConfig)}
        if self.field not in valid:
            raise ValueError(
                f"{self.field!r} is not a field on KeysConfig. "
                f"Valid fields: {sorted(valid)}"
            )


BINDING_GROUPS: list[tuple[str, list[BindingEntry]]] = [
    ("Navigation", [
        BindingEntry("Scroll down",     "scroll_down"),
        BindingEntry("Scroll up",       "scroll_up"),
        BindingEntry("Jump to top",     "jump_to_top"),
        BindingEntry("Jump to bottom",  "jump_to_bottom"),
    ]),
    ("Search", [
        BindingEntry("Open search",     "search"),
        BindingEntry("Next match",      "next_match"),
        BindingEntry("Previous match",  "prev_match"),
    ]),
    ("Panes", [
        BindingEntry("Open detail pane",    "open_pane"),
        BindingEntry("Horizontal split",    "horizontal_split"),
        BindingEntry("Vertical split",      "vertical_split"),
        BindingEntry("Floating modal",      "floating_split"),
    ]),
    ("General", [
        BindingEntry("Toggle mouse capture", "mouse_toggle"),
        BindingEntry("Show this help",       "help"),
        BindingEntry("Quit",                 "quit"),
    ]),
]
