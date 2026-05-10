# Config System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a TOML config system that loads `~/.config/aperture/config.toml`, creates it from bundled defaults on first run, and exposes a typed `ApertureConfig` to the app.

**Architecture:** A `config/` package added alongside toolong's existing modules. `schema.py` defines typed dataclasses with all defaults. `loader.py` reads the TOML file (creating it on first run from a bundled `defaults.toml`), maps hyphenated TOML keys to Python field names, validates enum values, and returns an `ApertureConfig`. `UI.__init__` calls `load_config()` and stores the result as `self.aperture_config`.

**Tech Stack:** Python 3.8+, `tomllib` (stdlib, Python 3.11+) / `tomli` (backport, Python <3.11), `pathlib`, `dataclasses`, `pytest`

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Modify | Add `tomli` conditional dependency |
| `src/toolong/config/__init__.py` | Create | Package init — exports `load_config`, `ApertureConfig` |
| `src/toolong/config/schema.py` | Create | `ThemeConfig`, `KeysConfig`, `PanesConfig`, `ApertureConfig` dataclasses with defaults |
| `src/toolong/config/loader.py` | Create | `load_config()`, `_build_config()`, hyphen→underscore key mapping |
| `src/toolong/config/defaults.toml` | Create | Bundled default config written to `~/.config/aperture/` on first run |
| `tests/__init__.py` | Create | Package marker |
| `tests/config/__init__.py` | Create | Package marker |
| `tests/config/test_schema.py` | Create | Schema default value tests |
| `tests/config/test_loader.py` | Create | Load, merge, first-run creation, validation tests |
| `src/toolong/ui.py` | Modify | Call `load_config()` in `UI.__init__`, store as `self.aperture_config` |

---

### Task 1: Scaffolding

**Files:**
- Modify: `pyproject.toml`
- Create: `src/toolong/config/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/config/__init__.py`

- [ ] **Step 1: Add tomli dependency**

In `pyproject.toml`, under `[tool.poetry.dependencies]`, add:

```toml
tomli = {version = "^2.0", python = "<3.11"}
```

- [ ] **Step 2: Install dependency**

```bash
cd /workspace/aperture && poetry install
```

Expected: resolves and installs `tomli` on Python < 3.11; no-op on 3.11+.

- [ ] **Step 3: Create package and test skeletons**

```bash
cd /workspace/aperture
mkdir -p src/toolong/config tests/config
touch src/toolong/config/__init__.py tests/__init__.py tests/config/__init__.py
```

- [ ] **Step 4: Commit scaffold**

```bash
cd /workspace/aperture
git add pyproject.toml poetry.lock src/toolong/config/__init__.py tests/__init__.py tests/config/__init__.py
git commit -m "chore: scaffold config package and test structure"
```

---

### Task 2: Config Schema

**Files:**
- Create: `src/toolong/config/schema.py`
- Test: `tests/config/test_schema.py`

- [ ] **Step 1: Write failing tests**

Create `tests/config/test_schema.py`:

```python
from toolong.config.schema import (
    ApertureConfig, KeysConfig, PanesConfig, ThemeConfig, VALID_SPLITS,
)


def test_theme_defaults_to_all_none():
    t = ThemeConfig()
    for attr in (
        "accent", "background", "foreground", "panel_background",
        "panel_foreground", "border", "primary", "secondary",
        "warning", "error", "success", "info",
    ):
        assert getattr(t, attr) is None, f"ThemeConfig.{attr} should default to None"


def test_keys_defaults():
    k = KeysConfig()
    assert k.scroll_down == "j"
    assert k.scroll_up == "k"
    assert k.jump_to_top == "g"
    assert k.jump_to_bottom == "G"
    assert k.search == "/"
    assert k.next_match == "n"
    assert k.prev_match == "N"
    assert k.open_pane == "enter"
    assert k.horizontal_split == "s"
    assert k.vertical_split == "v"
    assert k.floating_split == "f"
    assert k.mouse_toggle == "m"
    assert k.help == "?"
    assert k.quit == "q"


def test_panes_defaults():
    assert PanesConfig().default_split == "horizontal"


def test_aperture_config_composes_sections():
    config = ApertureConfig()
    assert isinstance(config.theme, ThemeConfig)
    assert isinstance(config.keys, KeysConfig)
    assert isinstance(config.panes, PanesConfig)


def test_valid_splits():
    assert VALID_SPLITS == {"horizontal", "vertical", "floating"}
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /workspace/aperture && poetry run pytest tests/config/test_schema.py -v
```

Expected: `ModuleNotFoundError: No module named 'toolong.config.schema'`

- [ ] **Step 3: Implement schema**

Create `src/toolong/config/schema.py`:

```python
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
```

- [ ] **Step 4: Run to verify passing**

```bash
cd /workspace/aperture && poetry run pytest tests/config/test_schema.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /workspace/aperture
git add src/toolong/config/schema.py tests/config/test_schema.py
git commit -m "feat: add ApertureConfig schema dataclasses"
```

---

### Task 3: TOML Loader

**Files:**
- Create: `src/toolong/config/defaults.toml`
- Create: `src/toolong/config/loader.py`
- Modify: `src/toolong/config/__init__.py`
- Test: `tests/config/test_loader.py`

- [ ] **Step 1: Write failing tests**

Create `tests/config/test_loader.py`:

```python
import pytest
from pathlib import Path

from toolong.config.loader import load_config
from toolong.config.schema import ApertureConfig


def write_toml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "config.toml"
    p.write_text(content, encoding="utf-8")
    return p


def test_empty_sections_return_defaults(tmp_path):
    p = write_toml(tmp_path, "[theme]\n[keys]\n[panes]\n")
    config = load_config(config_path=p)
    assert isinstance(config, ApertureConfig)
    assert config.keys.scroll_down == "j"
    assert config.panes.default_split == "horizontal"
    assert config.theme.accent is None


def test_overrides_key_binding(tmp_path):
    p = write_toml(tmp_path, '[keys]\nscroll-down = "J"\n')
    config = load_config(config_path=p)
    assert config.keys.scroll_down == "J"
    assert config.keys.scroll_up == "k"  # still default


def test_overrides_all_hyphenated_key_names(tmp_path):
    content = (
        '[keys]\n'
        'scroll-up = "K"\n'
        'jump-to-top = "gg"\n'
        'jump-to-bottom = "GG"\n'
        'next-match = "N2"\n'
        'prev-match = "P"\n'
        'open-pane = "o"\n'
        'horizontal-split = "h"\n'
        'vertical-split = "V"\n'
        'floating-split = "F"\n'
        'mouse-toggle = "M"\n'
    )
    p = write_toml(tmp_path, content)
    config = load_config(config_path=p)
    assert config.keys.scroll_up == "K"
    assert config.keys.jump_to_top == "gg"
    assert config.keys.jump_to_bottom == "GG"
    assert config.keys.next_match == "N2"
    assert config.keys.prev_match == "P"
    assert config.keys.open_pane == "o"
    assert config.keys.horizontal_split == "h"
    assert config.keys.vertical_split == "V"
    assert config.keys.floating_split == "F"
    assert config.keys.mouse_toggle == "M"


def test_overrides_theme_variable(tmp_path):
    p = write_toml(tmp_path, '[theme]\naccent = "#d65d0e"\n')
    config = load_config(config_path=p)
    assert config.theme.accent == "#d65d0e"
    assert config.theme.background is None


def test_overrides_pane_split(tmp_path):
    p = write_toml(tmp_path, '[panes]\ndefault-split = "floating"\n')
    config = load_config(config_path=p)
    assert config.panes.default_split == "floating"


def test_invalid_split_raises(tmp_path):
    p = write_toml(tmp_path, '[panes]\ndefault-split = "diagonal"\n')
    with pytest.raises(ValueError, match="Invalid panes.default-split"):
        load_config(config_path=p)


def test_first_run_creates_config_file(tmp_path):
    config_path = tmp_path / "aperture" / "config.toml"
    assert not config_path.exists()
    config = load_config(config_path=config_path)
    assert config_path.exists()
    assert isinstance(config, ApertureConfig)


def test_first_run_file_is_loadable_on_second_call(tmp_path):
    config_path = tmp_path / "aperture" / "config.toml"
    load_config(config_path=config_path)
    config2 = load_config(config_path=config_path)
    assert isinstance(config2, ApertureConfig)
    assert config2.keys.scroll_down == "j"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /workspace/aperture && poetry run pytest tests/config/test_loader.py -v
```

Expected: `ModuleNotFoundError: No module named 'toolong.config.loader'`

- [ ] **Step 3: Create defaults.toml**

Create `src/toolong/config/defaults.toml`:

```toml
# Aperture Configuration
# Location: ~/.config/aperture/config.toml

[theme]
# Optional: override individual Textual CSS variables for UI chrome
# accent = "#d65d0e"
# background = "#fbf1c7"
# foreground = "#282828"
# panel_background = "#f9f5d9"
# panel_foreground = "#282828"
# border = "#d65d0e"
# primary = "#d65d0e"
# secondary = "#8ec07c"
# warning = "#fabd2f"
# error = "#fb4934"
# success = "#b8bb26"
# info = "#83a598"

[keys]
# Navigation
scroll-down    = "j"
scroll-up      = "k"
jump-to-top    = "g"
jump-to-bottom = "G"

# Search
search         = "/"
next-match     = "n"
prev-match     = "N"

# Pane management
open-pane        = "enter"
horizontal-split = "s"
vertical-split   = "v"
floating-split   = "f"

# General
mouse-toggle = "m"
help         = "?"
quit         = "q"

[panes]
default-split = "horizontal"  # horizontal | vertical | floating
```

- [ ] **Step 4: Implement loader**

Create `src/toolong/config/loader.py`:

```python
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
```

- [ ] **Step 5: Update `__init__.py`**

Replace the contents of `src/toolong/config/__init__.py` with:

```python
from toolong.config.loader import load_config
from toolong.config.schema import ApertureConfig, KeysConfig, PanesConfig, ThemeConfig

__all__ = ["load_config", "ApertureConfig", "KeysConfig", "PanesConfig", "ThemeConfig"]
```

- [ ] **Step 6: Run all config tests**

```bash
cd /workspace/aperture && poetry run pytest tests/config/ -v
```

Expected: all 13 tests PASS.

- [ ] **Step 7: Commit**

```bash
cd /workspace/aperture
git add src/toolong/config/ tests/config/test_loader.py
git commit -m "feat: implement TOML config loader with first-run file creation"
```

---

### Task 4: Wire into ui.py

**Files:**
- Modify: `src/toolong/ui.py:1-19` (imports), `src/toolong/ui.py:112-119` (`UI.__init__`)

The `UI` class has an explicit `__init__` at line 112 that ends with `super().__init__()` at line 119.

- [ ] **Step 1: Add import**

In `src/toolong/ui.py`, add to the existing import block (after line 5, `from pathlib import Path`):

```python
from toolong.config import load_config, ApertureConfig
```

- [ ] **Step 2: Load config in `UI.__init__`**

In `src/toolong/ui.py`, the `UI.__init__` currently reads (lines 112–119):

```python
def __init__(
    self, file_paths: list[str], merge: bool = False, save_merge: str | None = None
) -> None:
    self.file_paths = self.sort_paths(file_paths)
    self.merge = merge
    self.save_merge = save_merge
    self.watcher = get_watcher()
    super().__init__()
```

Add `self.aperture_config` assignment after `super().__init__()`:

```python
def __init__(
    self, file_paths: list[str], merge: bool = False, save_merge: str | None = None
) -> None:
    self.file_paths = self.sort_paths(file_paths)
    self.merge = merge
    self.save_merge = save_merge
    self.watcher = get_watcher()
    super().__init__()
    self.aperture_config: ApertureConfig = load_config()
```

- [ ] **Step 3: Verify the app starts**

```bash
cd /workspace/aperture && echo "test log line" | poetry run tl /dev/stdin
```

Expected: app opens normally (press `q` to quit). No errors on startup.

- [ ] **Step 4: Verify config file was created**

```bash
cat ~/.config/aperture/config.toml
```

Expected: full commented config file matching `defaults.toml`.

- [ ] **Step 5: Commit**

```bash
cd /workspace/aperture
git add src/toolong/ui.py
git commit -m "feat: load ApertureConfig on app startup"
```
