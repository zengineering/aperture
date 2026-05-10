import pytest
from pathlib import Path

from toolong.config.loader import load_config
from toolong.config.schema import ApertureConfig


def write_toml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "config.toml"
    p.write_text(content, encoding="utf-8")
    return p


def test_empty_sections_return_defaults(tmp_path):
    p = write_toml(tmp_path, "[theme]\n[keys]\n[panes]\n")
    config = load_config(config_path=p)
    assert isinstance(config, ApertureConfig)
    assert config.keys.scroll_down == "j"
    assert config.panes.default_split == "horizontal"
    assert config.theme.accent is None


def test_overrides_key_binding(tmp_path):
    p = write_toml(tmp_path, '[keys]\nscroll-down = "J"\n')
    config = load_config(config_path=p)
    assert config.keys.scroll_down == "J"
    assert config.keys.scroll_up == "k"  # still default


def test_overrides_all_hyphenated_key_names(tmp_path):
    content = (
        '[keys]\n'
        'scroll-up = "K"\n'
        'jump-to-top = "gg"\n'
        'jump-to-bottom = "GG"\n'
        'next-match = "N2"\n'
        'prev-match = "P"\n'
        'open-pane = "o"\n'
        'horizontal-split = "h"\n'
        'vertical-split = "V"\n'
        'floating-split = "F"\n'
        'mouse-toggle = "M"\n'
    )
    p = write_toml(tmp_path, content)
    config = load_config(config_path=p)
    assert config.keys.scroll_up == "K"
    assert config.keys.jump_to_top == "gg"
    assert config.keys.jump_to_bottom == "GG"
    assert config.keys.next_match == "N2"
    assert config.keys.prev_match == "P"
    assert config.keys.open_pane == "o"
    assert config.keys.horizontal_split == "h"
    assert config.keys.vertical_split == "V"
    assert config.keys.floating_split == "F"
    assert config.keys.mouse_toggle == "M"


def test_overrides_theme_variable(tmp_path):
    p = write_toml(tmp_path, '[theme]\naccent = "#d65d0e"\n')
    config = load_config(config_path=p)
    assert config.theme.accent == "#d65d0e"
    assert config.theme.background is None


def test_overrides_pane_split(tmp_path):
    p = write_toml(tmp_path, '[panes]\ndefault-split = "floating"\n')
    config = load_config(config_path=p)
    assert config.panes.default_split == "floating"


def test_invalid_split_raises(tmp_path):
    p = write_toml(tmp_path, '[panes]\ndefault-split = "diagonal"\n')
    with pytest.raises(ValueError, match="Invalid panes.default-split"):
        load_config(config_path=p)


def test_first_run_creates_config_file(tmp_path):
    config_path = tmp_path / "aperture" / "config.toml"
    assert not config_path.exists()
    config = load_config(config_path=config_path)
    assert config_path.exists()
    assert isinstance(config, ApertureConfig)


def test_first_run_file_is_loadable_on_second_call(tmp_path):
    config_path = tmp_path / "aperture" / "config.toml"
    load_config(config_path=config_path)
    config2 = load_config(config_path=config_path)
    assert isinstance(config2, ApertureConfig)
    assert config2.keys.scroll_down == "j"
