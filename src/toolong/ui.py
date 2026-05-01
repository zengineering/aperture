from __future__ import annotations

import locale

from pathlib import Path

from toolong.config import load_config, ApertureConfig

from rich import terminal_theme
from textual.app import App, ComposeResult

from toolong.theme import GRUVBOX_LIGHT_ANSI, GRUVBOX_LIGHT_SYNTAX
from textual.binding import Binding
from textual.lazy import Lazy
from textual.screen import Screen
from textual.widgets import TabbedContent, TabPane

from toolong.log_view import LogView
from toolong.watcher import get_watcher
from toolong.help import HelpScreen
from toolong.input import BIND_HELP, BIND_QUIT, BIND_MOUSE_TOGGLE


locale.setlocale(locale.LC_ALL, "")


class LogScreen(Screen):

    BINDINGS = [
        BIND_HELP,
        BIND_QUIT,
        BIND_MOUSE_TOGGLE,
    ]

    CSS = """
    LogScreen {
        layers: overlay;
        & TabPane {           
            padding: 0;
        }
        & Tabs:focus Underline > .underline--bar {
            color: $accent;
        }        
        Underline > .underline--bar {
            color: $panel;
        }
    }
    """

    def compose(self) -> ComposeResult:
        assert isinstance(self.app, UI)
        with TabbedContent():
            if self.app.merge and len(self.app.file_paths) > 1:
                tab_name = " + ".join(Path(path).name for path in self.app.file_paths)
                with TabPane(tab_name):
                    yield Lazy(
                        LogView(
                            self.app.file_paths,
                            self.app.watcher,
                            can_tail=False,
                        )
                    )
            else:
                for path in self.app.file_paths:
                    with TabPane(path):
                        yield Lazy(
                            LogView(
                                [path],
                                self.app.watcher,
                                can_tail=True,
                            )
                        )

    def on_mount(self) -> None:
        assert isinstance(self.app, UI)
        self.query("TabbedContent Tabs").set(display=len(self.query(TabPane)) > 1)
        active_pane = self.query_one(TabbedContent).active_pane
        if active_pane is not None:
            active_pane.query("LogView > LogLines").focus()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen())


from functools import total_ordering


@total_ordering
class CompareTokens:
    """Compare filenames."""

    def __init__(self, path: str) -> None:
        self.tokens = [
            int(token) if token.isdigit() else token.lower()
            for token in path.split("/")[-1].split(".")
        ]

    def __eq__(self, other: object) -> bool:
        return self.tokens == other.tokens

    def __lt__(self, other: CompareTokens) -> bool:
        for token1, token2 in zip(self.tokens, other.tokens):
            try:
                if token1 < token2:
                    return True
            except TypeError:
                if str(token1) < str(token2):
                    return True
        return len(self.tokens) < len(other.tokens)


class UI(App):
    """The top level App object."""

    _mouse_captured: bool = True

    @classmethod
    def sort_paths(cls, paths: list[str]) -> list[str]:
        return sorted(paths, key=CompareTokens)

    def __init__(
        self, file_paths: list[str], merge: bool = False, save_merge: str | None = None
    ) -> None:
        self.file_paths = self.sort_paths(file_paths)
        self.merge = merge
        self.save_merge = save_merge
        self.watcher = get_watcher()
        self._config_warning: str | None = None
        super().__init__()
        try:
            self.aperture_config: ApertureConfig = load_config()
        except Exception as exc:
            self.aperture_config = ApertureConfig()
            self._config_warning = f"Config error — using defaults. ({exc})"

    def action_toggle_mouse(self) -> None:
        if self._mouse_captured:
            self.capture_mouse(None)
            self._mouse_captured = False
        else:
            self.capture_mouse(self.focused or self)
            self._mouse_captured = True

    def action_quit(self) -> None:
        self.exit()

    async def on_mount(self) -> None:
        self.ansi_theme_light = GRUVBOX_LIGHT_ANSI
        self.console.push_theme(GRUVBOX_LIGHT_SYNTAX)
        await self.push_screen(LogScreen())
        self.screen.query("LogLines").focus()
        if self._config_warning:
            self.notify(self._config_warning, severity="warning", timeout=8)
        self.watcher.start()

    def on_unmount(self) -> None:
        self.watcher.close()
