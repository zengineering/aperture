from toolong.log_lines import LogLines
from toolong.log_view import LogView
from toolong.ui import LogScreen, UI


def _expanded_keys(bindings) -> set[str]:
    """Return all individual key names, expanding comma-separated combos."""
    keys = set()
    for b in bindings:
        for k in b.key.split(","):
            keys.add(k.strip())
    return keys


def _action_for_key(bindings, key: str) -> str | None:
    for b in bindings:
        if key in [k.strip() for k in b.key.split(",")]:
            return b.action
    return None


class TestLogLinesBindings:
    def test_s_removed(self):
        assert "s" not in _expanded_keys(LogLines.BINDINGS)

    def test_m_removed(self):
        assert "m" not in _expanded_keys(LogLines.BINDINGS)

    def test_M_removed(self):
        assert "M" not in _expanded_keys(LogLines.BINDINGS)

    def test_j_present(self):
        assert "j" in _expanded_keys(LogLines.BINDINGS)

    def test_k_present(self):
        assert "k" in _expanded_keys(LogLines.BINDINGS)

    def test_g_maps_to_scroll_home(self):
        action = _action_for_key(LogLines.BINDINGS, "g")
        assert action == "scroll_home", f"g should map to scroll_home (top), got {action!r}"

    def test_G_maps_to_scroll_end(self):
        action = _action_for_key(LogLines.BINDINGS, "G")
        assert action == "scroll_end", f"G should map to scroll_end (bottom), got {action!r}"

    def test_arrows_still_present(self):
        keys = _expanded_keys(LogLines.BINDINGS)
        assert "up" in keys
        assert "down" in keys
        assert "left" in keys
        assert "right" in keys

    def test_home_end_present(self):
        keys = _expanded_keys(LogLines.BINDINGS)
        assert "home" in keys, "home key should still navigate to top"
        assert "end" in keys, "end key should still navigate to bottom"


class TestLogViewBindings:
    def test_slash_search_present(self):
        assert "slash" in _expanded_keys(LogView.BINDINGS)

    def test_n_present(self):
        assert "n" in _expanded_keys(LogView.BINDINGS)

    def test_N_present(self):
        assert "N" in _expanded_keys(LogView.BINDINGS)

    def test_n_maps_to_next_match(self):
        action = _action_for_key(LogView.BINDINGS, "n")
        assert action == "next_match"

    def test_N_maps_to_prev_match(self):
        action = _action_for_key(LogView.BINDINGS, "N")
        assert action == "prev_match"

    def test_slash_maps_to_show_find_dialog(self):
        action = _action_for_key(LogView.BINDINGS, "slash")
        assert action == "show_find_dialog"

    def test_action_next_match_advances_forward(self):
        from unittest.mock import MagicMock, patch
        view = LogView.__new__(LogView)
        mock_log_lines = MagicMock()
        with patch.object(LogView, "query_one", return_value=mock_log_lines):
            view.action_next_match()
        mock_log_lines.advance_search.assert_called_once_with(1)

    def test_action_prev_match_advances_backward(self):
        from unittest.mock import MagicMock, patch
        view = LogView.__new__(LogView)
        mock_log_lines = MagicMock()
        with patch.object(LogView, "query_one", return_value=mock_log_lines):
            view.action_prev_match()
        mock_log_lines.advance_search.assert_called_once_with(-1)


class TestLogScreenBindings:
    def test_help_key_is_question_mark(self):
        from toolong.config.schema import KeysConfig
        assert KeysConfig().help == "?"

    def test_f1_not_present(self):
        assert "f1" not in _expanded_keys(LogScreen.BINDINGS)

    def test_q_maps_to_quit(self):
        from toolong.config.schema import KeysConfig
        assert KeysConfig().quit == "q"

    def test_m_maps_to_toggle_mouse(self):
        from toolong.config.schema import KeysConfig
        assert KeysConfig().mouse_toggle == "m"


class TestUIActions:
    def test_action_toggle_mouse_exists(self):
        assert callable(getattr(UI, "action_toggle_mouse", None))

    def test_mouse_captured_default_true(self):
        ui = UI(file_paths=[])
        assert ui._mouse_captured is True
