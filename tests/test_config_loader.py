from __future__ import annotations

from toolong.ui import CompareTokens
from unittest.mock import patch, MagicMock
from textual.app import ScreenStackError
from toolong.ui import UI


class TestCompareTokens:
    def test_eq_with_non_compare_tokens_returns_not_implemented(self):
        ct = CompareTokens("foo.log")
        result = ct.__eq__("some string")
        assert result is NotImplemented

    def test_eq_with_non_compare_tokens_does_not_raise(self):
        ct = CompareTokens("foo.log")
        assert ct != "some string"
        assert ct != 42
        assert ct != None  # noqa: E711


class TestMouseToggle:
    def _make_ui(self) -> UI:
        with patch("toolong.ui.load_config"):
            ui = UI(file_paths=[])
        ui._mouse_captured = False
        return ui

    def test_mouse_state_unchanged_when_capture_raises(self):
        """If capture_mouse raises ScreenStackError, _mouse_captured must not flip."""
        ui = self._make_ui()
        with patch.object(ui, "capture_mouse", side_effect=ScreenStackError()):
            with patch.object(type(ui), "screen", create=True, new_callable=lambda: MagicMock()):
                ui.action_toggle_mouse()
        assert ui._mouse_captured is False

    def test_mouse_state_flips_on_successful_capture(self):
        """If capture_mouse succeeds, _mouse_captured must flip to True."""
        ui = self._make_ui()
        with patch.object(ui, "capture_mouse"):
            with patch.object(type(ui), "screen", create=True, new_callable=lambda: MagicMock()):
                ui.action_toggle_mouse()
        assert ui._mouse_captured is True

    def test_mouse_state_flips_false_on_release(self):
        """When _mouse_captured is True, action_toggle_mouse must flip it to False."""
        ui = self._make_ui()
        ui._mouse_captured = True
        with patch.object(ui, "capture_mouse"):
            with patch.object(type(ui), "screen", create=True, new_callable=lambda: MagicMock()):
                ui.action_toggle_mouse()
        assert ui._mouse_captured is False

    def test_release_calls_capture_mouse_with_none(self):
        """The release path must call capture_mouse(None), not with a widget."""
        ui = self._make_ui()
        ui._mouse_captured = True
        with patch.object(ui, "capture_mouse") as mock_capture:
            with patch.object(type(ui), "screen", create=True, new_callable=lambda: MagicMock()):
                ui.action_toggle_mouse()
        mock_capture.assert_called_once_with(None)


import pytest
from pathlib import Path
from toolong.config.loader import load_config


class TestLoadConfigFirstRun:
    def test_write_failure_raises_oserror_with_helpful_message(self, tmp_path):
        """A write failure during first-run setup must raise OSError with a clear message."""
        config_path = tmp_path / "sub" / "config.toml"
        config_path.parent.mkdir()
        config_path.parent.chmod(0o444)  # read-only — write will fail
        try:
            with pytest.raises(OSError, match="Failed to create default config"):
                load_config(config_path)
        finally:
            config_path.parent.chmod(0o755)  # restore so tmp_path cleanup works

    def test_first_run_creates_config_file(self, tmp_path):
        """When config does not exist, load_config creates it from defaults."""
        config_path = tmp_path / "config.toml"
        assert not config_path.exists()
        result = load_config(config_path)
        assert config_path.exists()
        assert result is not None


import tomllib


class TestUIConfigErrorHandling:
    def test_malformed_toml_falls_back_to_defaults(self):
        """A config file with invalid TOML must produce a warning, not a crash."""
        with patch("toolong.ui.load_config", side_effect=tomllib.TOMLDecodeError("bad", "", 0)):
            ui = UI(file_paths=[])
        assert ui.aperture_config is not None
        assert ui._config_warning is not None
        assert "config" in ui._config_warning.lower()


from toolong.config.loader import _build_config, _KEYS_MAP


class TestKeysMap:
    def test_all_hyphenated_toml_keys_map_to_valid_keys_config_fields(self):
        """Every value in _KEYS_MAP must be a real field on KeysConfig."""
        import dataclasses
        from toolong.config.schema import KeysConfig
        valid_fields = {f.name for f in dataclasses.fields(KeysConfig)}
        for toml_key, python_field in _KEYS_MAP.items():
            assert python_field in valid_fields, (
                f"_KEYS_MAP maps {toml_key!r} → {python_field!r}, "
                f"but {python_field!r} is not a field on KeysConfig"
            )

    def test_hyphenated_key_in_toml_is_translated(self):
        """A config with 'scroll-down = x' must set keys.scroll_down = 'x'."""
        raw = {"keys": {"scroll-down": "x"}}
        config = _build_config(raw)
        assert config.keys.scroll_down == "x"

    def test_all_hyphenated_keys_are_translated(self):
        """All _KEYS_MAP entries round-trip through _build_config correctly."""
        raw_keys = {toml_key: f"key_{i}" for i, toml_key in enumerate(_KEYS_MAP)}
        raw = {"keys": raw_keys}
        config = _build_config(raw)
        for toml_key, python_field in _KEYS_MAP.items():
            expected = raw_keys[toml_key]
            actual = getattr(config.keys, python_field)
            assert actual == expected, (
                f"_KEYS_MAP[{toml_key!r}] = {python_field!r}: "
                f"expected {expected!r}, got {actual!r}"
            )


class TestBuildConfigValidation:
    def test_invalid_split_raises_value_error(self):
        """_build_config must raise ValueError for an unrecognised panes.default-split."""
        raw = {"panes": {"default-split": "diagonal"}}
        with pytest.raises(ValueError, match="diagonal"):
            _build_config(raw)

    def test_valid_splits_are_accepted(self):
        """All three valid split values must be accepted without error."""
        for split in ("horizontal", "vertical", "floating"):
            raw = {"panes": {"default-split": split}}
            config = _build_config(raw)
            assert config.panes.default_split == split

    def test_default_split_is_horizontal(self):
        """When panes section is absent, default_split defaults to 'horizontal'."""
        config = _build_config({})
        assert config.panes.default_split == "horizontal"


class TestUITypeErrorPropagates:
    def test_type_error_in_load_config_propagates(self):
        """TypeError from a programming bug must not be silently swallowed as a config warning."""
        from unittest.mock import patch
        from toolong.ui import UI
        with patch("toolong.ui.load_config", side_effect=TypeError("internal bug")):
            with pytest.raises(TypeError, match="internal bug"):
                UI(file_paths=[])


class TestLoadConfigErrorMessages:
    def test_toml_decode_error_includes_file_path(self, tmp_path):
        """When TOML is malformed, the error message must include the config file path."""
        bad_config = tmp_path / "config.toml"
        bad_config.write_text("[invalid toml\n", encoding="utf-8")
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]
        with pytest.raises(Exception, match=str(bad_config)):
            load_config(bad_config)
