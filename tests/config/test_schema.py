from toolong.config.schema import (
    ApertureConfig, KeysConfig, PanesConfig, ThemeConfig, VALID_SPLITS,
)


def test_theme_defaults_to_all_none():
    t = ThemeConfig()
    for attr in (
        "accent", "background", "foreground", "panel_background",
        "panel_foreground", "border", "primary", "secondary",
        "warning", "error", "success", "info",
    ):
        assert getattr(t, attr) is None, f"ThemeConfig.{attr} should default to None"


def test_keys_defaults():
    k = KeysConfig()
    assert k.scroll_down == "j"
    assert k.scroll_up == "k"
    assert k.jump_to_top == "g"
    assert k.jump_to_bottom == "G"
    assert k.search == "/"
    assert k.next_match == "n"
    assert k.prev_match == "N"
    assert k.open_pane == "enter"
    assert k.horizontal_split == "s"
    assert k.vertical_split == "v"
    assert k.floating_split == "f"
    assert k.mouse_toggle == "m"
    assert k.help == "?"
    assert k.quit == "q"


def test_panes_defaults():
    assert PanesConfig().default_split == "horizontal"


def test_aperture_config_composes_sections():
    config = ApertureConfig()
    assert isinstance(config.theme, ThemeConfig)
    assert isinstance(config.keys, KeysConfig)
    assert isinstance(config.panes, PanesConfig)


def test_valid_splits():
    assert VALID_SPLITS == {"horizontal", "vertical", "floating"}
