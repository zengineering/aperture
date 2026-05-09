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
