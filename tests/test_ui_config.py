from unittest.mock import patch

from toolong.config.schema import ApertureConfig
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
