# Config Error Handling Design

**Date:** 2026-04-25
**Branch:** feature/config-system
**Scope:** Graceful degradation when `load_config()` fails at app startup

---

## Goal

When config loading fails for any reason, the app falls back to `ApertureConfig()` defaults and surfaces a warning toast notification inside the running TUI. The user can still use the tool; they are informed of the problem and its location.

---

## Architecture

Three touch points, no new modules, no new exception types.

### `loader.py` — no changes

`load_config()` continues to raise on all failure modes. The UI layer owns the fallback decision. Existing error paths:

- `tomllib.TOMLDecodeError` — malformed user config file
- `ValueError` — invalid `panes.default-split` value (already well-worded)
- `FileNotFoundError` — bundled `defaults.toml` missing (packaging bug)
- `PermissionError` — config directory not writable
- `OSError` — general I/O failure

### `ui.py` — `UI.__init__`

Wrap `load_config()` in `try/except`. On any failure, fall back to `ApertureConfig()` and store the error message. `aperture_config` is always set after `__init__`, including during `compose()`.

```python
self._config_warning: str | None = None
try:
    self.aperture_config = load_config()
except Exception as exc:
    self.aperture_config = ApertureConfig()
    self._config_warning = f"Config error — using defaults. ({exc})"
```

### `ui.py` — `on_mount`

Fire a Textual warning toast if a warning was captured. `on_mount` is used (not `__init__`) because it runs after the Textual event loop and screen are fully initialized.

```python
if self._config_warning:
    self.notify(self._config_warning, severity="warning", timeout=8)
```

---

## Error Messages

| Failure | What the user sees in the toast |
|---------|--------------------------------|
| Corrupted TOML | `Config error — using defaults. (Invalid value at line N)` |
| Bad `default-split` value | `Config error — using defaults. (Invalid panes.default-split 'foo'. Must be one of: floating, horizontal, vertical)` |
| Permission denied | `Config error — using defaults. (Permission denied: '/home/user/.config/aperture/config.toml')` |
| Missing bundled defaults | `Config error — using defaults. (No such file or directory: '.../defaults.toml')` |
| Any other OSError | `Config error — using defaults. (<os error message>)` |

The `f"Config error — using defaults. ({exc})"` format is used for all cases — the exception message already carries the specifics without per-type formatting.

---

## What Is Out of Scope

- `cli.py`'s `except Exception: pass` — pre-existing toolong behavior, not touched
- Type validation of config values (wrong types in TOML, e.g. `scroll-down = 42`) — separate concern
- Unknown key warnings — separate concern
- `loader.py` changes — no modifications needed

---

## Testing

Existing tests are unchanged. New tests cover the UI fallback behavior:

- `load_config()` raising `tomllib.TOMLDecodeError` → `aperture_config` is `ApertureConfig()`, `_config_warning` is set
- `load_config()` raising `PermissionError` → same
- `load_config()` raising `ValueError` → same
- `load_config()` succeeding → `_config_warning` is `None`

These are unit tests on `UI.__init__` using `unittest.mock.patch` on `load_config`.
