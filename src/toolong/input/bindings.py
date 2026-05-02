from __future__ import annotations

from textual.binding import Binding

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
