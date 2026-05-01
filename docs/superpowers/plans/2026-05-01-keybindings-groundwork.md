# Keybindings Groundwork Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `input/bindings.py` constants registry, wire it into existing widgets, fix toolong's inverted `g`/`G` bindings, and remove conflicting keys (`s`, `m`, `M`).

**Architecture:** A flat module `input/bindings.py` exports one `KEY_*` string constant and one pre-built `BIND_*` `Binding` object per key. Widgets import `BIND_*` objects directly into their `BINDINGS` class attribute. Config-driven runtime overrides are deferred to a future phase.

**Tech Stack:** Python 3.11+, Textual (`textual.binding.Binding`), pytest

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `src/toolong/input/__init__.py` | Re-exports all `KEY_*` and `BIND_*` names |
| Create | `src/toolong/input/bindings.py` | String constants + pre-built `Binding` objects |
| Modify | `src/toolong/log_lines.py` | Use `BIND_*` imports; fix g/G; remove s, m, M |
| Modify | `src/toolong/log_view.py` | Use `BIND_SEARCH`, add `BIND_NEXT_MATCH`/`BIND_PREV_MATCH`; add stubs |
| Modify | `src/toolong/ui.py` | Replace F1 with `?`; add quit and mouse-toggle bindings + actions |
| Create | `tests/input/__init__.py` | Makes tests/input a package |
| Create | `tests/input/test_bindings.py` | Registry correctness tests |
| Create | `tests/test_widget_bindings.py` | Widget BINDINGS state tests |

---

## Task 1: Create `input/bindings.py` with tests (TDD)

**Files:**
- Create: `tests/input/__init__.py`
- Create: `tests/input/test_bindings.py`
- Create: `src/toolong/input/__init__.py`
- Create: `src/toolong/input/bindings.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/input/__init__.py` (empty file), then create `tests/input/test_bindings.py`:

```python
import pytest
from toolong.input import (
    KEY_SCROLL_DOWN, BIND_SCROLL_DOWN,
    KEY_SCROLL_UP, BIND_SCROLL_UP,
    KEY_JUMP_TO_TOP, BIND_JUMP_TO_TOP,
    KEY_JUMP_TO_BOTTOM, BIND_JUMP_TO_BOTTOM,
    KEY_SEARCH, BIND_SEARCH,
    KEY_NEXT_MATCH, BIND_NEXT_MATCH,
    KEY_PREV_MATCH, BIND_PREV_MATCH,
    KEY_MOUSE_TOGGLE, BIND_MOUSE_TOGGLE,
    KEY_HELP, BIND_HELP,
    KEY_QUIT, BIND_QUIT,
)

ALL_BINDS = [
    (KEY_SCROLL_DOWN,    BIND_SCROLL_DOWN),
    (KEY_SCROLL_UP,      BIND_SCROLL_UP),
    (KEY_JUMP_TO_TOP,    BIND_JUMP_TO_TOP),
    (KEY_JUMP_TO_BOTTOM, BIND_JUMP_TO_BOTTOM),
    (KEY_SEARCH,         BIND_SEARCH),
    (KEY_NEXT_MATCH,     BIND_NEXT_MATCH),
    (KEY_PREV_MATCH,     BIND_PREV_MATCH),
    (KEY_MOUSE_TOGGLE,   BIND_MOUSE_TOGGLE),
    (KEY_HELP,           BIND_HELP),
    (KEY_QUIT,           BIND_QUIT),
]


@pytest.mark.parametrize("key_const, binding", ALL_BINDS)
def test_binding_key_matches_constant(key_const, binding):
    assert binding.key == key_const


def test_no_duplicate_keys():
    keys = [b.key for _, b in ALL_BINDS]
    assert len(keys) == len(set(keys)), f"Duplicate keys found: {keys}"


def test_key_constants_have_expected_values():
    assert KEY_SCROLL_DOWN    == "j"
    assert KEY_SCROLL_UP      == "k"
    assert KEY_JUMP_TO_TOP    == "g"
    assert KEY_JUMP_TO_BOTTOM == "G"
    assert KEY_SEARCH         == "slash"
    assert KEY_NEXT_MATCH     == "n"
    assert KEY_PREV_MATCH     == "N"
    assert KEY_MOUSE_TOGGLE   == "m"
    assert KEY_HELP           == "?"
    assert KEY_QUIT           == "q"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /workspace/aperture && python -m pytest tests/input/test_bindings.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'toolong.input'`

- [ ] **Step 3: Create `src/toolong/input/__init__.py`**

```python
from toolong.input.bindings import (
    KEY_SCROLL_DOWN, BIND_SCROLL_DOWN,
    KEY_SCROLL_UP, BIND_SCROLL_UP,
    KEY_JUMP_TO_TOP, BIND_JUMP_TO_TOP,
    KEY_JUMP_TO_BOTTOM, BIND_JUMP_TO_BOTTOM,
    KEY_SEARCH, BIND_SEARCH,
    KEY_NEXT_MATCH, BIND_NEXT_MATCH,
    KEY_PREV_MATCH, BIND_PREV_MATCH,
    KEY_MOUSE_TOGGLE, BIND_MOUSE_TOGGLE,
    KEY_HELP, BIND_HELP,
    KEY_QUIT, BIND_QUIT,
)

__all__ = [
    "KEY_SCROLL_DOWN", "BIND_SCROLL_DOWN",
    "KEY_SCROLL_UP", "BIND_SCROLL_UP",
    "KEY_JUMP_TO_TOP", "BIND_JUMP_TO_TOP",
    "KEY_JUMP_TO_BOTTOM", "BIND_JUMP_TO_BOTTOM",
    "KEY_SEARCH", "BIND_SEARCH",
    "KEY_NEXT_MATCH", "BIND_NEXT_MATCH",
    "KEY_PREV_MATCH", "BIND_PREV_MATCH",
    "KEY_MOUSE_TOGGLE", "BIND_MOUSE_TOGGLE",
    "KEY_HELP", "BIND_HELP",
    "KEY_QUIT", "BIND_QUIT",
]
```

- [ ] **Step 4: Create `src/toolong/input/bindings.py`**

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd /workspace/aperture && python -m pytest tests/input/test_bindings.py -v
```

Expected: 12 passed

- [ ] **Step 6: Commit**

```bash
cd /workspace/aperture && git add src/toolong/input/ tests/input/ && git commit -m "feat: add input/bindings.py constants registry"
```

---

## Task 2: Update `log_lines.py` BINDINGS

**Files:**
- Create: `tests/test_widget_bindings.py`
- Modify: `src/toolong/log_lines.py`

**Note:** Toolong's `"up,w,k"` and `"down,s,j"` combos must be split. `k` and `j` are extracted into their own `BIND_*` objects; the combos become `"up,w"` and `"down"` respectively. This avoids duplicate key registrations that would cause unpredictable behavior in Textual.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_widget_bindings.py`:

```python
from toolong.log_lines import LogLines


def _expanded_keys(bindings) -> set[str]:
    """Return all individual key names, expanding comma-separated combos."""
    keys = set()
    for b in bindings:
        for k in b.key.split(","):
            keys.add(k.strip())
    return keys


def _action_for_key(bindings, key: str) -> str | None:
    for b in bindings:
        if key in [k.strip() for k in b.key.split(",")]:
            return b.action
    return None


class TestLogLinesBindings:
    def test_s_removed(self):
        assert "s" not in _expanded_keys(LogLines.BINDINGS)

    def test_m_removed(self):
        assert "m" not in _expanded_keys(LogLines.BINDINGS)

    def test_M_removed(self):
        assert "M" not in _expanded_keys(LogLines.BINDINGS)

    def test_j_present(self):
        assert "j" in _expanded_keys(LogLines.BINDINGS)

    def test_k_present(self):
        assert "k" in _expanded_keys(LogLines.BINDINGS)

    def test_g_maps_to_scroll_home(self):
        action = _action_for_key(LogLines.BINDINGS, "g")
        assert action == "scroll_home", f"g should map to scroll_home (top), got {action!r}"

    def test_G_maps_to_scroll_end(self):
        action = _action_for_key(LogLines.BINDINGS, "G")
        assert action == "scroll_end", f"G should map to scroll_end (bottom), got {action!r}"

    def test_arrows_still_present(self):
        keys = _expanded_keys(LogLines.BINDINGS)
        assert "up" in keys
        assert "down" in keys
        assert "left" in keys
        assert "right" in keys
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /workspace/aperture && python -m pytest tests/test_widget_bindings.py -v
```

Expected: `test_s_removed` FAIL, `test_m_removed` FAIL, `test_M_removed` FAIL, `test_g_maps_to_scroll_home` FAIL, `test_G_maps_to_scroll_end` FAIL (toolong has g/G inverted)

- [ ] **Step 3: Update `log_lines.py` BINDINGS**

Open `src/toolong/log_lines.py`. Add this import near the top (after existing imports):

```python
from toolong.input import (
    BIND_SCROLL_DOWN,
    BIND_SCROLL_UP,
    BIND_JUMP_TO_TOP,
    BIND_JUMP_TO_BOTTOM,
)
```

Replace the entire `BINDINGS` class attribute (currently lines 131–147) with:

```python
    BINDINGS = [
        Binding("up,w", "scroll_up", "Scroll Up", show=False),
        BIND_SCROLL_UP,
        Binding("down", "scroll_down", "Scroll Down", show=False),
        BIND_SCROLL_DOWN,
        Binding("left,h", "scroll_left", "Scroll Left", show=False),
        Binding("right,l", "scroll_right", "Scroll Right", show=False),
        BIND_JUMP_TO_TOP,
        BIND_JUMP_TO_BOTTOM,
        Binding("pageup,b", "page_up", "Page Up", show=False),
        Binding("pagedown,space", "page_down", "Page Down", show=False),
        Binding("enter", "select", "Select line", show=False),
        Binding("escape", "dismiss", "Dismiss", show=False, priority=True),
        Binding("o", "navigate(+1, 'h')"),
        Binding("O", "navigate(-1, 'h')"),
        Binding("d", "navigate(+1, 'd')"),
        Binding("D", "navigate(-1, 'd')"),
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /workspace/aperture && python -m pytest tests/test_widget_bindings.py -v
```

Expected: all 9 `TestLogLinesBindings` tests pass

- [ ] **Step 5: Run the full test suite to check for regressions**

```bash
cd /workspace/aperture && python -m pytest --tb=short -q
```

Expected: all previously passing tests still pass

- [ ] **Step 6: Commit**

```bash
cd /workspace/aperture && git add src/toolong/log_lines.py tests/test_widget_bindings.py && git commit -m "feat: wire log_lines.py to input registry; fix g/G inversion; remove s, m, M conflicts"
```

---

## Task 3: Update `log_view.py` BINDINGS and add stubs

**Files:**
- Modify: `src/toolong/log_view.py`
- Modify: `tests/test_widget_bindings.py`

- [ ] **Step 1: Add failing tests to `tests/test_widget_bindings.py`**

Append to the file:

```python
from toolong.log_view import LogView


class TestLogViewBindings:
    def test_slash_search_present(self):
        assert "slash" in _expanded_keys(LogView.BINDINGS)

    def test_n_present(self):
        assert "n" in _expanded_keys(LogView.BINDINGS)

    def test_N_present(self):
        assert "N" in _expanded_keys(LogView.BINDINGS)

    def test_n_maps_to_next_match(self):
        action = _action_for_key(LogView.BINDINGS, "n")
        assert action == "next_match"

    def test_N_maps_to_prev_match(self):
        action = _action_for_key(LogView.BINDINGS, "N")
        assert action == "prev_match"

    def test_stub_action_next_match_exists(self):
        assert callable(getattr(LogView, "action_next_match", None))

    def test_stub_action_prev_match_exists(self):
        assert callable(getattr(LogView, "action_prev_match", None))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /workspace/aperture && python -m pytest tests/test_widget_bindings.py::TestLogViewBindings -v
```

Expected: `test_n_present` FAIL, `test_N_present` FAIL, `test_stub_action_next_match_exists` FAIL, `test_stub_action_prev_match_exists` FAIL

- [ ] **Step 3: Update `log_view.py`**

Open `src/toolong/log_view.py`. Add this import near the top:

```python
from toolong.input import BIND_SEARCH, BIND_NEXT_MATCH, BIND_PREV_MATCH
```

Replace the `BINDINGS` class attribute (currently lines 276–281) with:

```python
    BINDINGS = [
        Binding("ctrl+t", "toggle_tail", "Tail", key_display="^t"),
        Binding("ctrl+l", "toggle('show_line_numbers')", "Line nos.", key_display="^l"),
        Binding("ctrl+f", "show_find_dialog", "Find", key_display="^f"),
        BIND_SEARCH,
        Binding("ctrl+g", "goto", "Go to", key_display="^g"),
        BIND_NEXT_MATCH,
        BIND_PREV_MATCH,
    ]
```

Then add these two stub methods to the `LogView` class (anywhere after `__init__`, before the end of the class):

```python
    def action_next_match(self) -> None:
        pass  # implemented in search wiring phase

    def action_prev_match(self) -> None:
        pass  # implemented in search wiring phase
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /workspace/aperture && python -m pytest tests/test_widget_bindings.py::TestLogViewBindings -v
```

Expected: all 7 `TestLogViewBindings` tests pass

- [ ] **Step 5: Run the full test suite**

```bash
cd /workspace/aperture && python -m pytest --tb=short -q
```

Expected: all previously passing tests still pass

- [ ] **Step 6: Commit**

```bash
cd /workspace/aperture && git add src/toolong/log_view.py tests/test_widget_bindings.py && git commit -m "feat: wire log_view.py search bindings; add n/N stubs"
```

---

## Task 4: Update `ui.py` — help, quit, and mouse toggle

**Files:**
- Modify: `src/toolong/ui.py`
- Modify: `tests/test_widget_bindings.py`

- [ ] **Step 1: Add failing tests to `tests/test_widget_bindings.py`**

Append to the file:

```python
from toolong.ui import LogScreen, UI


class TestLogScreenBindings:
    def test_help_key_is_question_mark(self):
        action = _action_for_key(LogScreen.BINDINGS, "?")
        assert action == "help"

    def test_f1_not_present(self):
        assert "f1" not in _expanded_keys(LogScreen.BINDINGS)

    def test_q_maps_to_quit(self):
        action = _action_for_key(LogScreen.BINDINGS, "q")
        assert action == "quit"

    def test_m_maps_to_toggle_mouse(self):
        action = _action_for_key(LogScreen.BINDINGS, "m")
        assert action == "toggle_mouse"


class TestUIActions:
    def test_action_toggle_mouse_exists(self):
        assert callable(getattr(UI, "action_toggle_mouse", None))

    def test_mouse_captured_default_true(self):
        # Class-level default — no app instantiation needed
        assert UI._mouse_captured is True
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /workspace/aperture && python -m pytest tests/test_widget_bindings.py::TestLogScreenBindings tests/test_widget_bindings.py::TestUIActions -v
```

Expected: `test_help_key_is_question_mark` FAIL (currently F1), `test_f1_not_present` FAIL, `test_q_maps_to_quit` FAIL, `test_m_maps_to_toggle_mouse` FAIL, `test_action_toggle_mouse_exists` FAIL

- [ ] **Step 3: Update `ui.py`**

Open `src/toolong/ui.py`. Add to the existing imports from `toolong.input`:

```python
from toolong.input import BIND_HELP, BIND_QUIT, BIND_MOUSE_TOGGLE
```

Replace `LogScreen.BINDINGS`:

```python
    BINDINGS = [
        BIND_HELP,
        BIND_QUIT,
        BIND_MOUSE_TOGGLE,
    ]
```

Add `_mouse_captured` and the two action methods to the `UI` class (before `on_mount`):

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

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /workspace/aperture && python -m pytest tests/test_widget_bindings.py::TestLogScreenBindings tests/test_widget_bindings.py::TestUIActions -v
```

Expected: all 6 tests pass

- [ ] **Step 5: Run the full test suite**

```bash
cd /workspace/aperture && python -m pytest --tb=short -q
```

Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
cd /workspace/aperture && git add src/toolong/ui.py tests/test_widget_bindings.py && git commit -m "feat: wire ui.py keybindings; add mouse toggle and quit actions"
```
