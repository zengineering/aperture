import pytest
from rich.theme import Theme
from rich.terminal_theme import TerminalTheme

from toolong.theme import GRUVBOX_LIGHT_SYNTAX, GRUVBOX_LIGHT_ANSI


# ---------------------------------------------------------------------------
# Layer 2: Rich syntax theme
# ---------------------------------------------------------------------------

def test_gruvbox_light_syntax_is_rich_theme():
    assert isinstance(GRUVBOX_LIGHT_SYNTAX, Theme)


def _color_name(theme: Theme, style_name: str) -> str:
    return theme.styles[style_name].color.name


def test_repr_number_is_yellow():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.number") == "#d79921"


def test_repr_bool_true_is_green():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.bool_true") == "#98971a"


def test_repr_bool_false_is_red():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.bool_false") == "#cc241d"


def test_repr_none_is_orange():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.none") == "#d65d0e"


def test_repr_str_is_green():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.str") == "#98971a"


def test_repr_uuid_is_blue():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.uuid") == "#458588"


def test_repr_ipv4_is_aqua():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.ipv4") == "#689d6a"


def test_repr_ipv6_is_aqua():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.ipv6") == "#689d6a"


def test_repr_eui48_is_aqua():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.eui48") == "#689d6a"


def test_repr_eui64_is_aqua():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.eui64") == "#689d6a"


def test_repr_path_is_blue():
    assert _color_name(GRUVBOX_LIGHT_SYNTAX, "repr.path") == "#458588"


# ---------------------------------------------------------------------------
# Layer 3: ANSI terminal theme
# ---------------------------------------------------------------------------

def test_gruvbox_light_ansi_is_terminal_theme():
    assert isinstance(GRUVBOX_LIGHT_ANSI, TerminalTheme)


def test_gruvbox_light_ansi_background():
    bg = GRUVBOX_LIGHT_ANSI.background_color
    assert (bg.red, bg.green, bg.blue) == (251, 241, 199)  # #fbf1c7


def test_gruvbox_light_ansi_foreground():
    fg = GRUVBOX_LIGHT_ANSI.foreground_color
    assert (fg.red, fg.green, fg.blue) == (40, 40, 40)  # #282828
