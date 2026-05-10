from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Label

from toolong.config.schema import KeysConfig
from toolong.input.bindings import BINDING_GROUPS


class ApertureHelpScreen(ModalScreen):
    """Modal help screen — shows all active keybindings grouped by context."""

    BINDINGS = [Binding("escape,q", "dismiss", "Close")]

    DEFAULT_CSS = """
    ApertureHelpScreen {
        align: center middle;
    }
    ApertureHelpScreen VerticalScroll {
        width: 60;
        height: auto;
        max-height: 80%;
        border: round $accent;
        padding: 1 2;
    }
    ApertureHelpScreen .help-group {
        text-style: bold;
        margin-top: 1;
        color: $accent;
    }
    ApertureHelpScreen .help-entry {
        padding-left: 2;
    }
    """

    def __init__(self, keys: KeysConfig) -> None:
        super().__init__()
        self._keys = keys

    def compose(self) -> ComposeResult:
        with VerticalScroll() as vs:
            vs.border_title = "Key Bindings"
            vs.border_subtitle = "ESCAPE to dismiss"
            for group_name, entries in BINDING_GROUPS:
                yield Label(group_name, classes="help-group")
                for entry in entries:
                    key_val = getattr(self._keys, entry.field)
                    yield Label(
                        f"{key_val:<12}{entry.label}",
                        classes="help-entry",
                    )
