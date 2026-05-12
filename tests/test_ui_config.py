from unittest.mock import patch

from toolong.config.schema import ApertureConfig, ThemeConfig
from toolong.ui import UI


def test_config_success_sets_no_warning():
    """Happy path: load_config succeeds, no warning stored."""
    with patch("toolong.ui.load_config", return_value=ApertureConfig()):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is None


def test_config_value_error_falls_back_to_defaults():
    """Invalid config value: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=ValueError("Invalid panes.default-split 'bad'. Must be one of: floating, horizontal, vertical"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "Invalid panes.default-split" in ui._config_warning


def test_config_permission_error_falls_back_to_defaults():
    """Unwritable config dir: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=PermissionError("[Errno 13] Permission denied: '/home/user/.config/aperture'"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "Permission denied" in ui._config_warning


def test_config_file_not_found_falls_back_to_defaults():
    """Missing bundled defaults.toml: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=FileNotFoundError("[Errno 2] No such file or directory: '/path/to/defaults.toml'"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "No such file" in ui._config_warning


def test_config_os_error_falls_back_to_defaults():
    """General I/O error: falls back to defaults, warning stored."""
    with patch(
        "toolong.ui.load_config",
        side_effect=OSError("disk read error"),
    ):
        ui = UI([])
    assert isinstance(ui.aperture_config, ApertureConfig)
    assert ui._config_warning is not None
    assert "Config error" in ui._config_warning
    assert "disk read error" in ui._config_warning


def test_warning_message_format():
    """Warning message includes file path and recovery instructions."""
    with patch(
        "toolong.ui.load_config",
        side_effect=ValueError("bad value"),
    ):
        ui = UI([])
    assert "~/.config/aperture/config.toml" in ui._config_warning
    assert "Delete the file to reset" in ui._config_warning
    assert "bad value" in ui._config_warning


def _run_on_mount(ui: UI) -> None:
    """Run on_mount with all Textual side-effects mocked out."""
    import asyncio
    from unittest.mock import AsyncMock, MagicMock, PropertyMock

    with (
        patch.object(ui, "push_screen", new_callable=AsyncMock),
        patch.object(ui, "console", MagicMock()),
        patch.object(type(ui), "screen", new_callable=PropertyMock, return_value=MagicMock()),
        patch.object(ui.watcher, "start"),
    ):
        asyncio.run(ui.on_mount())


def test_on_mount_notifies_on_warning():
    """When _config_warning is set, on_mount calls notify with the right args."""
    with patch("toolong.ui.load_config", side_effect=ValueError("bad value")):
        ui = UI([])

    with patch.object(ui, "notify") as mock_notify:
        _run_on_mount(ui)

    mock_notify.assert_called_once()
    call_kwargs = mock_notify.call_args
    assert "Config error" in call_kwargs.args[0]
    assert call_kwargs.kwargs.get("severity") == "warning"
    assert call_kwargs.kwargs.get("timeout") == 8


def test_on_mount_does_not_notify_on_success():
    """When _config_warning is None, on_mount does not call notify."""
    with patch("toolong.ui.load_config", return_value=ApertureConfig()):
        ui = UI([])

    with patch.object(ui, "notify") as mock_notify:
        _run_on_mount(ui)

    mock_notify.assert_not_called()


def _ui_with_theme(**theme_kwargs) -> UI:
    """Construct a UI whose ThemeConfig has the given fields set."""
    config = ApertureConfig(theme=ThemeConfig(**theme_kwargs))
    with patch("toolong.ui.load_config", return_value=config):
        return UI([])


def test_get_css_variables_accent_override():
    """A non-None ThemeConfig.accent appears in get_css_variables()."""
    ui = _ui_with_theme(accent="#ff0000")
    variables = ui.get_css_variables()
    assert variables["accent"] == "#ff0000"


def test_get_css_variables_panel_background_hyphen():
    """panel_background (underscore) maps to panel-background (hyphen) in CSS."""
    ui = _ui_with_theme(panel_background="#eeeeee")
    variables = ui.get_css_variables()
    assert variables["panel-background"] == "#eeeeee"
    assert "panel_background" not in variables


def test_get_css_variables_none_fields_not_overridden():
    """Fields left as None must not overwrite theme defaults."""
    ui = _ui_with_theme()  # all None
    variables = ui.get_css_variables()
    assert all(v is not None for v in variables.values())


def test_get_css_variables_multiple_overrides():
    """Multiple non-None fields are all applied."""
    ui = _ui_with_theme(primary="#aabbcc", error="#dd0000", success="#00bb44")
    variables = ui.get_css_variables()
    assert variables["primary"] == "#aabbcc"
    assert variables["error"] == "#dd0000"
    assert variables["success"] == "#00bb44"


def test_get_css_variables_partial_override_preserves_others():
    """Setting one field does not clobber unrelated CSS variables."""
    ui_default = _ui_with_theme()
    ui_override = _ui_with_theme(accent="#123456")
    default_vars = ui_default.get_css_variables()
    override_vars = ui_override.get_css_variables()
    assert override_vars["accent"] == "#123456"
    for key, val in default_vars.items():
        if key != "accent":
            assert override_vars.get(key) == val, f"Unexpected change in {key!r}"
