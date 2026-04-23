# Aperture — Design Spec

**Date:** 2026-04-22
**Project:** aperture
**Base:** Fork of [toolong](https://github.com/textualize/toolong) (Textual/Python TUI)

---

## Overview

Aperture is a fork of toolong — a terminal log viewer built on Textual — with four primary differentiators:

1. Gruvbox-light theme (with general theme customization support)
2. Vim-inspired keybindings with a `?` help screen
3. Versatile pane splits (horizontal, vertical, floating) for detail views
4. Mouse mode toggle for native terminal text selection/copy

The goal is maximum upstream compatibility with toolong on log I/O, file tailing, and parsing. New features are isolated in dedicated modules to minimize rebase friction.

---

## Architecture

Aperture adds four new modules alongside toolong's existing code. Toolong's core modules (`log_file.py`, `watcher.py`, `format_parser.py`, `highlighter.py`, etc.) are left untouched where possible.

```
aperture/
  config/       # TOML config loading, validation, defaults
  theme/        # Token → Textual CSS + Pygments style wiring
  input/        # Keybinding registry + ? help screen
  panes/        # Split/float pane orchestration
  # ...existing toolong modules unchanged...
```

The app entry point (`ui.py`) is the integration point: it loads config, applies the theme, registers keybindings, and initializes the pane system before handing off to Textual's run loop.

**Upstream tracking:** toolong is added as a git remote. Rebasing upstream changes will surface conflicts primarily at `ui.py` and any screen/widget files where keybindings or layout are wired up. The module boundaries keep this surface minimal.

---

## Theme System

Aperture's theme system has three layers, each mapped to a different library:

### Layer 1: UI Chrome — Textual built-in theme

Textual ships a built-in `gruvbox` theme. Aperture sets this as the default:

```python
class ApertureApp(App):
    THEME = "gruvbox"
```

Users can override individual Textual CSS variables in config (see below).

### Layer 2: Log Syntax Highlighting — Rich Theme

Toolong's `LogHighlighter` uses Rich's `RegexHighlighter`, which applies `repr.*` named styles (e.g., `repr.number`, `repr.bool_true`, `repr.str`) from Rich's theme system — not Pygments. These styles control colors for IPs, UUIDs, booleans, numbers, and strings within log lines.

Aperture defines a custom Rich `Theme` mapping `repr.*` styles to gruvbox-light colors and passes it to the Textual app. This theme is bundled as the default and is not user-configurable in v1 (users who want to customize log syntax colors can modify the source or override via a future `[theme.syntax]` config section).

### Layer 3: ANSI-Colored Logs — terminal palette

Toolong sets `ansi_theme_dark = terminal_theme.DIMMED_MONOKAI`. Aperture defines a gruvbox-light 16-color ANSI palette and sets it as the default `ansi_theme_light`.

### Config

```toml
[theme]
# Optional: override individual Textual CSS variables
# accent = "#d65d0e"
# background = "#fbf1c7"
```

The config file is created at `~/.config/aperture/config.toml` on first run from a bundled default. The gruvbox-light Rich theme for log syntax highlighting is bundled and applied automatically — no config needed for the default experience.

---

## Keybindings

All bindings are centralized in `input/bindings.py` as named constants. Textual's `BINDINGS` declarations on each widget reference these constants — no scattered hardcoded keys.

### Default Bindings

| Key | Action |
|-----|--------|
| `j` / `k` | Scroll down / up |
| `g` | Jump to top |
| `G` | Jump to bottom |
| `/` | Open search |
| `n` / `N` | Next / previous search match |
| `Enter` | Open detail pane (default split from config) |
| `s` | Open detail pane — horizontal split |
| `v` | Open detail pane — vertical split |
| `f` | Open detail pane — floating |
| `m` | Toggle mouse capture |
| `?` | Open keybinding help screen |
| `q` | Quit |

### Conflict Resolution

Toolong's existing bindings were audited against all proposed keys (`log_lines.py`, `log_view.py`, `find_dialog.py`). Resolutions:

| Key | Toolong binding | Resolution |
|-----|----------------|------------|
| `j` / `k` | scroll_down / scroll_up | Compatible — same action, retained as-is |
| `/` | show_find_dialog | Compatible — same action, retained as-is |
| `Enter` | select (open detail) | Compatible — same action, retained as-is |
| `g` | scroll_end (**bottom**) | **Override** — toolong has g/G inverted from vim convention; Aperture corrects to vim standard (g=top, G=bottom) |
| `G` | scroll_home (**top**) | **Override** — same inversion; Aperture corrects to vim standard |
| `s` | scroll_down alias | **Remove** toolong's `s` alias; `j` and arrow keys remain for scrolling |
| `m` | navigate forward by minute | **Remove** toolong's `m`/`M` minute-navigation bindings; mouse toggle takes precedence |
| `n` / `N` | unbound | No conflict |
| `v` / `f` / `?` / `q` | unbound | No conflict |

### Help Screen

`?` opens a modal overlay listing all active bindings grouped by context (Navigation, Search, Panes, General). The overlay is generated dynamically from the binding registry so it stays in sync with any config overrides automatically.

### Config

```toml
[keys]
scroll-down = "j"
scroll-up   = "k"
search      = "/"
help        = "?"
# etc.
```

---

## Pane System

The `panes/` module wraps toolong's existing `LinePanel` (`src/toolong/line_panel.py:57`) with three layout modes for the detail view. `LinePanel` extends `ScrollableContainer` and uses only standard Textual APIs (`self.app.batch_update()`, `self.query()`, `self.mount()`) with no coupling to a specific parent widget — it can be placed in any container without modification.

| Mode | Layout | Key |
|------|--------|-----|
| `horizontal` | Detail pane below log view | `s` |
| `vertical` | Detail pane beside log view (toolong default) | `v` |
| `floating` | Centered modal overlay, dismiss with `Escape`/`q` | `f` |

`Enter` opens the detail pane in the default mode (configurable). If a detail pane is already open, pressing a different split key closes and reopens it in the new layout.

Pane sizing defaults to 50/50 and is not resizable in v1 — keeps implementation close to toolong's existing logic.

### Config

```toml
[panes]
default-split = "horizontal"  # horizontal | vertical | floating
```

---

## Mouse Mode

Textual captures mouse events by default. Aperture adds a toggle (`m`) that calls `self.app.capture_mouse(None)` to release mouse capture, allowing native terminal text selection and copy.

- **Mouse on** (default): Textual handles mouse — scrolling and clicking work in-app
- **Mouse off**: Terminal handles mouse — native text selection and copy

A footer indicator shows current state (e.g., `[MOUSE OFF]`).

This is a minimal implementation in `ui.py` — no new module needed.

---

## Complete Configuration Reference

The full `~/.config/aperture/config.toml` with all available options and defaults:

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
scroll-down    = "j"      # Scroll down one line
scroll-up      = "k"      # Scroll up one line
jump-to-top    = "g"      # Jump to the top of the log
jump-to-bottom = "G"      # Jump to the bottom of the log

# Search
search         = "/"      # Open search dialog
next-match     = "n"      # Jump to next search match
prev-match     = "N"      # Jump to previous search match

# Pane management
open-pane         = "enter"  # Open detail pane in default split mode
horizontal-split  = "s"      # Open detail pane — horizontal split
vertical-split    = "v"      # Open detail pane — vertical split
floating-split    = "f"      # Open detail pane — floating modal

# General
mouse-toggle   = "m"      # Toggle mouse capture on/off
help           = "?"      # Show keybinding help screen
quit           = "q"      # Quit Aperture

[panes]
default-split = "horizontal"  # Default split mode: horizontal | vertical | floating
```

The gruvbox-light Rich theme (log syntax highlighting) and ANSI palette are bundled defaults — no config entries are needed or exposed for these in v1.

---

## Out of Scope (v1)

- Modal editing (insert/normal mode switching)
- Resizable panes
- Plugin/extension system
- Multiple file tabs (inherited from toolong as-is)
- Remote log streaming
