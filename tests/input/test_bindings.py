import pytest
from toolong.input import (
    KEY_SCROLL_DOWN, BIND_SCROLL_DOWN,
    KEY_SCROLL_UP, BIND_SCROLL_UP,
    KEY_JUMP_TO_TOP, BIND_JUMP_TO_TOP,
    KEY_JUMP_TO_BOTTOM, BIND_JUMP_TO_BOTTOM,
    KEY_SEARCH, BIND_SEARCH,
    KEY_NEXT_MATCH, BIND_NEXT_MATCH,
    KEY_PREV_MATCH, BIND_PREV_MATCH,
    KEY_MOUSE_TOGGLE, BIND_MOUSE_TOGGLE,
    KEY_HELP, BIND_HELP,
    KEY_QUIT, BIND_QUIT,
)

ALL_BINDS = [
    (KEY_SCROLL_DOWN,    BIND_SCROLL_DOWN),
    (KEY_SCROLL_UP,      BIND_SCROLL_UP),
    (KEY_JUMP_TO_TOP,    BIND_JUMP_TO_TOP),
    (KEY_JUMP_TO_BOTTOM, BIND_JUMP_TO_BOTTOM),
    (KEY_SEARCH,         BIND_SEARCH),
    (KEY_NEXT_MATCH,     BIND_NEXT_MATCH),
    (KEY_PREV_MATCH,     BIND_PREV_MATCH),
    (KEY_MOUSE_TOGGLE,   BIND_MOUSE_TOGGLE),
    (KEY_HELP,           BIND_HELP),
    (KEY_QUIT,           BIND_QUIT),
]


@pytest.mark.parametrize("key_const, binding", ALL_BINDS)
def test_binding_key_matches_constant(key_const, binding):
    assert binding.key == key_const


def test_no_duplicate_keys():
    keys = [b.key for _, b in ALL_BINDS]
    assert len(keys) == len(set(keys)), f"Duplicate keys found: {keys}"


def test_key_constants_have_expected_values():
    assert KEY_SCROLL_DOWN    == "j"
    assert KEY_SCROLL_UP      == "k"
    assert KEY_JUMP_TO_TOP    == "g"
    assert KEY_JUMP_TO_BOTTOM == "G"
    assert KEY_SEARCH         == "slash"
    assert KEY_NEXT_MATCH     == "n"
    assert KEY_PREV_MATCH     == "N"
    assert KEY_MOUSE_TOGGLE   == "m"
    assert KEY_HELP           == "?"
    assert KEY_QUIT           == "q"
