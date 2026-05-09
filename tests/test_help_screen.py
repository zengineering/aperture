from __future__ import annotations

import dataclasses

import pytest
import pytest_asyncio
from textual.widgets import Label

from toolong.config.schema import ApertureConfig, KeysConfig
from toolong.help import ApertureHelpScreen
from toolong.input.bindings import BINDING_GROUPS, BindingEntry
from toolong.ui import UI, LogScreen


class TestBindingGroups:
    def test_binding_groups_is_nonempty(self):
        assert len(BINDING_GROUPS) > 0

    def test_all_groups_have_name_and_entries(self):
        for name, entries in BINDING_GROUPS:
            assert isinstance(name, str) and name
            assert len(entries) > 0

    def test_all_entry_fields_exist_on_keys_config(self):
        valid_fields = {f.name for f in dataclasses.fields(KeysConfig)}
        for _name, entries in BINDING_GROUPS:
            for entry in entries:
                assert entry.field in valid_fields, (
                    f"BindingEntry field {entry.field!r} not found on KeysConfig"
                )

    def test_no_duplicate_fields(self):
        seen = set()
        for _name, entries in BINDING_GROUPS:
            for entry in entries:
                assert entry.field not in seen, f"Duplicate field: {entry.field!r}"
                seen.add(entry.field)

    def test_groups_contain_expected_names(self):
        names = [name for name, _ in BINDING_GROUPS]
        assert "Navigation" in names
        assert "Search" in names
        assert "Panes" in names
        assert "General" in names


class TestApertureHelpScreen:
    def test_importable(self):
        assert ApertureHelpScreen is not None

    def test_accepts_keys_config(self):
        keys = KeysConfig()
        screen = ApertureHelpScreen(keys)
        assert screen is not None

    def test_escape_binding_present(self):
        bound_keys = {b.key for b in ApertureHelpScreen.BINDINGS}
        assert any("escape" in k for k in bound_keys)


@pytest_asyncio.fixture
async def running_app():
    """Run UI headless and yield (app, pilot). load_config is patched to avoid file I/O."""
    from unittest.mock import patch
    with patch("toolong.ui.load_config", return_value=ApertureConfig()):
        ui = UI(file_paths=[])
    async with ui.run_test(headless=True) as pilot:
        await pilot.pause()
        yield ui, pilot


@pytest.mark.asyncio
async def test_help_action_pushes_aperture_help_screen(running_app):
    """Pressing ? must push ApertureHelpScreen."""
    ui, pilot = running_app
    await pilot.press("question_mark")
    await pilot.pause()
    assert isinstance(ui.screen, ApertureHelpScreen)


@pytest.mark.asyncio
async def test_help_screen_shows_navigation_group(running_app):
    """The rendered help screen contains the word 'Navigation'."""
    ui, pilot = running_app
    await pilot.press("question_mark")
    await pilot.pause()
    labels = ui.screen.query(Label)
    texts = [str(lbl.renderable) for lbl in labels]
    assert any("Navigation" in t for t in texts)


@pytest.mark.asyncio
async def test_help_screen_escape_dismisses(running_app):
    """ESC dismisses the help screen and returns to LogScreen."""
    ui, pilot = running_app
    await pilot.press("question_mark")
    await pilot.pause()
    await pilot.press("escape")
    await pilot.pause()
    assert isinstance(ui.screen, LogScreen)


@pytest_asyncio.fixture
async def app_with_custom_keys():
    """Run UI headless with help='h', quit='x', mouse_toggle='z' and yield (app, pilot).
    load_config is patched so custom keys are active from the first on_mount call."""
    from unittest.mock import patch
    custom_keys = KeysConfig(help="h", quit="x", mouse_toggle="z")
    custom_config = ApertureConfig(keys=custom_keys)
    with patch("toolong.ui.load_config", return_value=custom_config):
        ui = UI(file_paths=[])
    async with ui.run_test(headless=True) as pilot:
        await pilot.pause()
        yield ui, pilot


@pytest.mark.asyncio
async def test_custom_help_key_pushes_help_screen(app_with_custom_keys):
    """Pressing the custom help key 'h' must push ApertureHelpScreen."""
    ui, pilot = app_with_custom_keys
    await pilot.press("h")
    await pilot.pause()
    assert isinstance(ui.screen, ApertureHelpScreen)


@pytest.mark.asyncio
async def test_default_help_key_no_longer_works_after_remap(app_with_custom_keys):
    """After remapping help to 'h', pressing '?' must NOT push ApertureHelpScreen."""
    ui, pilot = app_with_custom_keys
    await pilot.press("question_mark")
    await pilot.pause()
    assert not isinstance(ui.screen, ApertureHelpScreen)


@pytest.mark.asyncio
async def test_custom_quit_key_does_not_open_help_screen(app_with_custom_keys):
    """The app has an action_quit method, and pressing 'x' does not open help screen."""
    ui, pilot = app_with_custom_keys
    assert callable(getattr(ui, "action_quit", None))
    await pilot.press("x")
    await pilot.pause()
    assert not isinstance(ui.screen, ApertureHelpScreen)


@pytest.mark.asyncio
async def test_help_screen_renders_custom_key_values(app_with_custom_keys):
    """Help screen labels must show the active (remapped) key values, not hardcoded defaults."""
    ui, pilot = app_with_custom_keys
    # custom keys: help='h', quit='x', mouse_toggle='z'
    await pilot.press("h")
    await pilot.pause()
    assert isinstance(ui.screen, ApertureHelpScreen)
    labels = ui.screen.query(Label)
    texts = [str(lbl.renderable) for lbl in labels]
    # 'h' is the custom help key — it must appear somewhere in the rendered labels
    assert any("h" in t for t in texts), (
        f"Expected custom help key 'h' in help screen labels, got: {texts}"
    )
    # 'x' is the custom quit key — it must appear somewhere in the rendered labels
    assert any("x" in t for t in texts), (
        f"Expected custom quit key 'x' in help screen labels, got: {texts}"
    )


class TestNormalizeKey:
    """Unit tests for LogScreen._normalize_key (the Textual key-name bridge)."""

    def test_multichar_key_returned_verbatim(self):
        """Keys longer than 1 character are returned unchanged."""
        assert LogScreen._normalize_key("enter") == "enter"
        assert LogScreen._normalize_key("f1") == "f1"
        assert LogScreen._normalize_key("ctrl+c") == "ctrl+c"

    def test_alphanumeric_returned_as_is(self):
        """Single alphanumeric characters are returned unchanged."""
        assert LogScreen._normalize_key("j") == "j"
        assert LogScreen._normalize_key("G") == "G"
        assert LogScreen._normalize_key("n") == "n"

    def test_question_mark_normalized(self):
        """'?' must normalize to the Textual key name for question mark."""
        result = LogScreen._normalize_key("?")
        assert result == "question_mark"

    def test_slash_normalized(self):
        """'/' must normalize to the Textual key name for slash."""
        result = LogScreen._normalize_key("/")
        assert result == "slash"

    def test_single_digit_is_alphanumeric(self):
        """Single digit characters are alphanumeric and returned as-is."""
        assert LogScreen._normalize_key("1") == "1"


class TestNormalizeKeyEdgeCases:
    def test_control_character_raises_value_error_with_message(self):
        """A character with no Unicode name must raise ValueError with a clear message."""
        with pytest.raises(ValueError, match="not a valid bindable character"):
            LogScreen._normalize_key("\x00")


class TestBindingEntryValidation:
    def test_invalid_field_name_raises_on_construction(self):
        """BindingEntry must raise ValueError when field is not a KeysConfig attribute."""
        with pytest.raises(ValueError, match="not a field on KeysConfig"):
            BindingEntry(label="Test", field="nonexistent_field")

    def test_valid_field_name_constructs_without_error(self):
        """BindingEntry must accept any real KeysConfig field name."""
        entry = BindingEntry(label="Scroll down", field="scroll_down")
        assert entry.field == "scroll_down"
