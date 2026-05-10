from __future__ import annotations

from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen

from toolong.line_panel import LinePanel


class FloatingPane(ModalScreen):
    """A modal overlay that displays a log line detail in a centered LinePanel."""

    BINDINGS = [Binding("escape,q", "dismiss", "Close")]

    DEFAULT_CSS = """
    FloatingPane {
        align: center middle;
        LinePanel {
            width: 80%;
            height: 80%;
            border: heavy $accent;
        }
    }
    """

    def __init__(self, line: str, text: Text, timestamp: datetime | None) -> None:
        super().__init__()
        self._line = line
        self._text = text
        self._timestamp = timestamp

    def compose(self) -> ComposeResult:
        yield LinePanel()

    async def on_mount(self) -> None:
        await self.query_one(LinePanel).update(self._line, self._text, self._timestamp)
