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

### Layer 2: Log Syntax Highlighting — Pygments

Toolong uses Rich's `RegexHighlighter` with `repr.*` styles, and Rich delegates to Pygments for syntax highlighting. Pygments ships `GruvboxLightStyle` built-in.

Aperture sets the default Pygments style to `gruvbox-light` and makes it configurable via a single config key accepting any valid Pygments style name.

### Layer 3: ANSI-Colored Logs — terminal palette

Toolong sets `ansi_theme_dark = terminal_theme.DIMMED_MONOKAI`. Aperture defines a gruvbox-light 16-color ANSI palette and sets it as the default `ansi_theme_light`.

### Config

```toml
[theme]
# Pygments style for log syntax highlighting (any valid Pygments style name)
syntax-style = "gruvbox-light"

# Optional: override individual Textual CSS variables
# accent = "#d65d0e"
# background = "#fbf1c7"
```

The config file is created at `~/.config/aperture/config.toml` on first run from a bundled default. Users who want full customization can override any Textual CSS variable; most users only need `syntax-style`.

---

## Keybindings

All bindings are centralized in `input/bindings.py` as named constants. Textual's `BINDINGS` declarations on each widget reference these constants — no scattered hardcoded keys.

### Default Bindings

| Key | Action |
|-----|--------|
| `j` / `k` | Scroll down / up |
| `g g` | Jump to top |
| `G` | Jump to bottom |
| `/` | Open search |
| `n` / `p` | Next / previous search match |
| `Enter` | Open detail pane (default split from config) |
| `h` | Open detail pane — horizontal split |
| `v` | Open detail pane — vertical split |
| `f` | Open detail pane — floating |
| `m` | Toggle mouse capture |
| `?` | Open keybinding help screen |
| `q` | Quit |

Toolong's existing bindings that don't conflict are preserved.

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

The `panes/` module wraps toolong's existing `LinePanel` with three layout modes for the detail view:

| Mode | Layout | Key |
|------|--------|-----|
| `horizontal` | Detail pane below log view | `h` |
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

## Out of Scope (v1)

- Modal editing (insert/normal mode switching)
- Resizable panes
- Plugin/extension system
- Multiple file tabs (inherited from toolong as-is)
- Remote log streaming
