from unittest.mock import patch

import pytest

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
    """Warning message uses the expected format."""
    with patch(
        "toolong.ui.load_config",
        side_effect=ValueError("bad value"),
    ):
        ui = UI([])
    assert ui._config_warning == "Config error — using defaults. (bad value)"
