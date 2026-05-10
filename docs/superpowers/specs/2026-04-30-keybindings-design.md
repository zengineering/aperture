# Keybindings Groundwork — Design Spec

**Date:** 2026-04-30
**Project:** aperture
**Phase:** Groundwork — constants registry + widget wiring (config-driven overrides deferred)

---

## Overview

Creates the `input/` module with a flat constants registry (`input/bindings.py`), updates existing widgets to use it, corrects toolong's inverted `g`/`G` bindings, removes conflicting keys, and adds stub actions for new bindings. The `?` help screen and runtime config-driven key overrides are out of scope for this phase.

---

## Module Structure

```
src/toolong/input/
    __init__.py       # re-exports all BIND_* and KEY_* names
    bindings.py       # string constants + pre-built Binding objects
```

### `input/bindings.py`

Two exports per binding: a `KEY_*` string constant and a `BIND_*` `Binding` object. Widgets import `BIND_*` objects directly into their `BINDINGS` class attribute.

```python
from textual.binding import Binding

# Navigation
KEY_SCROLL_DOWN    = "j"
KEY_SCROLL_UP      = "k"
KEY_JUMP_TO_TOP    = "g"
KEY_JUMP_TO_BOTTOM = "G"

BIND_SCROLL_DOWN    = Binding(KEY_SCROLL_DOWN,    "scroll_down",    show=False)
BIND_SCROLL_UP      = Binding(KEY_SCROLL_UP,      "scroll_up",      show=False)
BIND_JUMP_TO_TOP    = Binding(KEY_JUMP_TO_TOP,    "scroll_home",    show=False)
BIND_JUMP_TO_BOTTOM = Binding(KEY_JUMP_TO_BOTTOM, "scroll_end",     show=False)

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
```

Pane bindings (`s`, `v`, `f`) are omitted — they belong to the `panes/` module.

### `input/__init__.py`

Re-exports all `BIND_*` and `KEY_*` names so call sites use:

```python
from toolong.input import BIND_SCROLL_DOWN, KEY_SCROLL_DOWN
```

---

## Changes to Existing Files

### `log_lines.py`

**Remove:**
- `"down,s,j"` combo — split; `s` freed for panes
- `"home,G"` / `"end,g"` — toolong has these inverted from vim convention
- `Binding("m", "navigate(+1, 'm')")` and `Binding("M", "navigate(-1, 'm')")` — minute-navigation removed; `m` taken by mouse toggle

**Replace with imports from `input/`:**
- `BIND_SCROLL_DOWN` (j only)
- `BIND_SCROLL_UP` (k only)
- `BIND_JUMP_TO_TOP` — `g` → `scroll_home` (vim: top)
- `BIND_JUMP_TO_BOTTOM` — `G` → `scroll_end` (vim: bottom)

**Keep unchanged:** `up,w,k`, `left,h`, `right,l`, `pageup,b`, `pagedown,space`, `enter`, `escape`, `o`/`O`/`d`/`D` navigate bindings.

### `log_view.py`

**Replace:**
- `Binding("slash", "show_find_dialog", ...)` → `BIND_SEARCH`

**Add:**
- `BIND_NEXT_MATCH`, `BIND_PREV_MATCH`

**Add stub actions on `LogView`:**
```python
def action_next_match(self) -> None:
    pass  # implemented in search wiring phase

def action_prev_match(self) -> None:
    pass
```

### `ui.py` / `LogScreen`

**Replace:**
- `Binding("f1", "help", "Help")` → `BIND_HELP` (key changes from F1 to `?`)

**Add to `LogScreen.BINDINGS`:**
- `BIND_QUIT`
- `BIND_MOUSE_TOGGLE`

**Add to `UI`:**
```python
_mouse_captured: bool = True

def action_toggle_mouse(self) -> None:
    if self._mouse_captured:
        self.capture_mouse(None)
        self._mouse_captured = False
    else:
        self.capture_mouse(self.focused or self)
        self._mouse_captured = True

def action_quit(self) -> None:
    self.exit()
```

---

## Conflict Resolution Summary

| Key | Toolong binding | Resolution |
|-----|----------------|------------|
| `g` | `scroll_end` (bottom) | **Override** — corrected to vim standard (g=top) |
| `G` | `scroll_home` (top) | **Override** — corrected to vim standard (G=bottom) |
| `s` | `scroll_down` alias | **Remove** — `j` and arrows remain; `s` freed for panes |
| `m` / `M` | minute-navigation | **Remove** — `m` taken by mouse toggle |
| `n` / `N` | unbound | No conflict — added as next/prev match |
| `?` / `q` | unbound | No conflict — added as help/quit |

---

## Tests

**`tests/input/test_bindings.py`:**

- Every `BIND_*` object's `.key` value matches its corresponding `KEY_*` constant
- No two `BIND_*` objects share the same key (collision check)
- `from toolong.input import *` smoke test — all expected names present

Tests are pure-Python with no Textual app instantiation.

---

## Out of Scope (this phase)

- Runtime config-driven key overrides (deferred — `KeysConfig` values not yet wired to `BINDINGS`)
- `?` help screen content (deferred to `input/` phase 2)
- Pane bindings (`s`, `v`, `f`, `enter`) — belong to `panes/` design
- Full `n`/`N` search implementation — stubs only
