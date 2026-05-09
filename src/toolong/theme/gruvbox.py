from rich.terminal_theme import TerminalTheme
from rich.theme import Theme

# Gruvbox-light palette
_YELLOW = "#d79921"
_GREEN = "#98971a"
_RED = "#cc241d"
_ORANGE = "#d65d0e"
_BLUE = "#458588"
_AQUA = "#689d6a"

GRUVBOX_LIGHT_SYNTAX = Theme({
    "repr.number": _YELLOW,
    "repr.bool_true": _GREEN,
    "repr.bool_false": _RED,
    "repr.none": _ORANGE,
    "repr.str": _GREEN,
    "repr.uuid": _BLUE,
    "repr.ipv4": _AQUA,
    "repr.ipv6": _AQUA,
    "repr.eui48": _AQUA,
    "repr.eui64": _AQUA,
    "repr.path": _BLUE,
})

GRUVBOX_LIGHT_ANSI = TerminalTheme(
    (251, 241, 199),  # background #fbf1c7
    (40, 40, 40),     # foreground #282828
    [
        (40, 40, 40),       # black   #282828
        (204, 36, 29),      # red     #cc241d
        (152, 151, 26),     # green   #98971a
        (215, 153, 33),     # yellow  #d79921
        (69, 133, 136),     # blue    #458588
        (177, 98, 134),     # magenta #b16286
        (104, 157, 106),    # cyan    #689d6a
        (168, 153, 132),    # white   #a89984
    ],
    [
        (146, 131, 116),    # bright black   #928374
        (157, 0, 6),        # bright red     #9d0006
        (121, 116, 14),     # bright green   #79740e
        (181, 118, 20),     # bright yellow  #b57614
        (7, 102, 120),      # bright blue    #076678
        (143, 63, 113),     # bright magenta #8f3f71
        (66, 123, 88),      # bright cyan    #427b58
        (235, 219, 178),    # bright white   #ebdbb2
    ],
)
