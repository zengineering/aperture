# Config Error Handling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When `load_config()` fails at startup, `UI` falls back to `ApertureConfig()` defaults and shows a Textual warning toast — the app always starts.

**Architecture:** `UI.__init__` wraps `load_config()` in `try/except`, falling back to `ApertureConfig()` and storing the error string in `self._config_warning`. `on_mount` fires `self.notify(...)` if that field is set. No changes to `loader.py`.

**Tech Stack:** Python 3.8+, Textual (`App.notify`), `unittest.mock.patch`, `pytest`

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `tests/test_ui_config.py` | Create | Unit tests for `UI.__init__` fallback behavior |
| `src/toolong/ui.py` | Modify | Add `try/except` in `__init__`, add notify call in `on_mount` |

---

### Task 1: Tests and Implementation

**Files:**
- Create: `tests/test_ui_config.py`
- Modify: `src/toolong/ui.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_ui_config.py`:

```python
from unittest.mock import patch

import pytest

from toolong.config.schema import ApertureConfig
from toolong.ui import UI


def test_config_success_sets_no_warning():
    """Happy path: load_config succeeds, no warning stored."""
    with patch("toolong.ui.load_config", return_value=ApertureConfig()):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is None


def test_config_value_error_falls_back_to_defaults():
    """Invalid config value: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=ValueError("Invalid panes.default-split 'bad'. Must be one of: floating, horizontal, vertical"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "Invalid panes.default-split" in ui._config_warning


def test_config_permission_error_falls_back_to_defaults():
    """Unwritable config dir: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=PermissionError("[Errno 13] Permission denied: '/home/user/.config/aperture'"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "Permission denied" in ui._config_warning


def test_config_file_not_found_falls_back_to_defaults():
    """Missing bundled defaults.toml: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=FileNotFoundError("[Errno 2] No such file or directory: '/path/to/defaults.toml'"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "No such file" in ui._config_warning


def test_config_os_error_falls_back_to_defaults():
    """General I/O error: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=OSError("disk read error"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "disk read error" in ui._config_warning


def test_warning_message_format():
    """Warning message uses the expected format."""
    with patch(
        "toolong.ui.load_config",
        side_effect=ValueError("bad value"),
    ):
        ui = UI([])
    assert ui._config_warning == "Config error — using defaults. (bad value)"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /workspace/aperture && poetry run pytest tests/test_ui_config.py -v
```

Expected: all 6 tests FAIL — either `AttributeError: 'UI' object has no attribute '_config_warning'` or the warning assertion fails because no fallback exists yet.

- [ ] **Step 3: Implement the error handling in `ui.py`**

In `src/toolong/ui.py`, update `UI.__init__` (currently lines 114–122):

```python
def __init__(
    self, file_paths: list[str], merge: bool = False, save_merge: str | None = None
) -> None:
    self.file_paths = self.sort_paths(file_paths)
    self.merge = merge
    self.save_merge = save_merge
    self.watcher = get_watcher()
    super().__init__()
    self._config_warning: str | None = None
    try:
        self.aperture_config: ApertureConfig = load_config()
    except Exception as exc:
        self.aperture_config = ApertureConfig()
        self._config_warning = f"Config error — using defaults. ({exc})"
```

Then update `on_mount` (currently lines 124–127) to add the notify call:

```python
async def on_mount(self) -> None:
    self.ansi_theme_dark = terminal_theme.DIMMED_MONOKAI
    await self.push_screen(LogScreen())
    self.screen.query("LogLines").focus()
    self.watcher.start()
    if self._config_warning:
        self.notify(self._config_warning, severity="warning", timeout=8)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /workspace/aperture && poetry run pytest tests/test_ui_config.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Run the full test suite to verify no regressions**

```bash
cd /workspace/aperture && poetry run pytest -v
```

Expected: all existing tests in `tests/config/test_loader.py` and `tests/config/test_schema.py` still PASS.

- [ ] **Step 6: Commit**

```bash
cd /workspace/aperture
git add tests/test_ui_config.py src/toolong/ui.py
git commit -m "feat: fall back to defaults with warning toast on config load failure"
```
