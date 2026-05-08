import pytest
from textual.widgets import Static
from toolong.ui import UI


@pytest.fixture
async def app():
    """Run UI headless and yield the running app."""
    ui = UI(file_paths=[])
    async with ui.run_test(headless=True) as pilot:
        await pilot.pause()
        yield ui


async def test_mouse_status_indicator_initial_state(app):
    """Indicator is empty on startup (mouse captured by default)."""
    indicator = app.screen.query_one("#mouse-status", Static)
    assert str(indicator.renderable) == ""


async def test_mouse_status_indicator_shows_when_off(app):
    """Indicator shows [MOUSE OFF] after toggle."""
    app.action_toggle_mouse()
    await app.workers.wait_for_complete()
    indicator = app.screen.query_one("#mouse-status", Static)
    assert str(indicator.renderable) == "[MOUSE OFF]"


async def test_mouse_status_indicator_clears_when_restored(app):
    """Indicator clears after toggling back on."""
    app.action_toggle_mouse()
    app.action_toggle_mouse()
    await app.workers.wait_for_complete()
    indicator = app.screen.query_one("#mouse-status", Static)
    assert str(indicator.renderable) == ""


def test_ui_theme_is_gruvbox():
    """UI class must declare gruvbox as the default Textual theme."""
    assert UI.THEME == "gruvbox"


def test_config_toml_error_falls_back_to_defaults(tmp_path, monkeypatch):
    """A malformed config TOML should trigger fallback, not crash."""
    bad_toml = tmp_path / "config.toml"
    bad_toml.write_text("this is not [ valid toml !!!", encoding="utf-8")
    monkeypatch.setattr("toolong.config.loader._CONFIG_PATH", bad_toml)
    ui = UI(file_paths=[])
    assert ui.aperture_config is not None
    assert ui._config_warning is not None
    assert "config.toml" in ui._config_warning


def test_toggle_mouse_does_not_raise_before_screen_mounted():
    """action_toggle_mouse must not propagate exceptions if DOM is not ready."""
    ui = UI(file_paths=[])
    try:
        ui.action_toggle_mouse()
    except Exception as exc:
        pytest.fail(f"action_toggle_mouse raised unexpectedly: {exc}")
