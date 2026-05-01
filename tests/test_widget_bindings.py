from toolong.log_lines import LogLines


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
