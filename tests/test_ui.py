import asyncio
import pytest
from textual.widgets import Static
from toolong.ui import UI


class _AppHandle:
    """Wraps a running UI app, routing query_one through the active screen."""

    def __init__(self, app):
        self._app = app

    def query_one(self, selector, widget_type=None):
        if widget_type is not None:
            return self._app.screen.query_one(selector, widget_type)
        return self._app.screen.query_one(selector)

    def action_toggle_mouse(self):
        return self._app.action_toggle_mouse()


@pytest.fixture
def app():
    """Run UI headless, yield a handle for synchronous test access."""
    ui = UI(file_paths=[])

    async def run():
        async with ui.run_test(headless=True) as pilot:
            await pilot.pause()
            yield _AppHandle(ui)

    loop = asyncio.new_event_loop()
    gen = run()
    try:
        handle = loop.run_until_complete(gen.__anext__())
        yield handle
    finally:
        try:
            loop.run_until_complete(gen.aclose())
        except Exception:
            pass
        loop.close()


def test_mouse_status_indicator_initial_state(app):
    """Indicator is empty on startup (mouse captured by default)."""
    indicator = app.query_one("#mouse-status", Static)
    assert str(indicator.renderable) == ""


def test_mouse_status_indicator_shows_when_off(app):
    """Indicator shows [MOUSE OFF] after toggle."""
    app.action_toggle_mouse()
    indicator = app.query_one("#mouse-status", Static)
    assert str(indicator.renderable) == "[MOUSE OFF]"


def test_mouse_status_indicator_clears_when_restored(app):
    """Indicator clears after toggling back on."""
    app.action_toggle_mouse()
    app.action_toggle_mouse()
    indicator = app.query_one("#mouse-status", Static)
    assert str(indicator.renderable) == ""


def test_ui_theme_is_gruvbox():
    """UI class must declare gruvbox as the default Textual theme."""
    assert UI.THEME == "gruvbox"
