import pytest
from rich.text import Text

from toolong.panes import FloatingPane
from toolong.line_panel import LinePanel
from toolong.ui import UI


@pytest.fixture
async def app_pilot(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("hello world\n", encoding="utf-8")
    app = UI(file_paths=[str(log_file)])
    async with app.run_test(headless=True) as pilot:
        await pilot.pause()
        await pilot.pause(0.1)
        yield app, pilot


async def test_floating_pane_contains_line_panel(app_pilot):
    """FloatingPane must mount a LinePanel widget."""
    app, pilot = app_pilot
    pane = FloatingPane("hello world", Text("hello world"), None)
    await app.push_screen(pane)
    await pilot.pause()
    assert app.screen.query_one(LinePanel) is not None


async def test_floating_pane_is_modal(app_pilot):
    """FloatingPane must be the active screen after being pushed."""
    app, pilot = app_pilot
    pane = FloatingPane("some line", Text("some line"), None)
    await app.push_screen(pane)
    await pilot.pause()
    assert isinstance(app.screen, FloatingPane)


async def test_floating_pane_dismisses_on_escape(app_pilot):
    """Pressing Escape must dismiss the FloatingPane and restore the previous screen."""
    app, pilot = app_pilot
    previous_screen = app.screen
    pane = FloatingPane("some line", Text("some line"), None)
    await app.push_screen(pane)
    await pilot.pause()
    await pilot.press("escape")
    await pilot.pause()
    assert app.screen is previous_screen


async def test_floating_pane_dismisses_on_q(app_pilot):
    """Pressing q must dismiss the FloatingPane."""
    app, pilot = app_pilot
    previous_screen = app.screen
    pane = FloatingPane("some line", Text("some line"), None)
    await app.push_screen(pane)
    await pilot.pause()
    await pilot.press("q")
    await pilot.pause()
    assert app.screen is previous_screen
