from __future__ import annotations

import dataclasses
from toolong.input.bindings import BINDING_GROUPS, BindingEntry
from toolong.config.schema import KeysConfig


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
        seen = []
        for _name, entries in BINDING_GROUPS:
            for entry in entries:
                assert entry.field not in seen, f"Duplicate field: {entry.field!r}"
                seen.append(entry.field)

    def test_groups_contain_expected_names(self):
        names = [name for name, _ in BINDING_GROUPS]
        assert "Navigation" in names
        assert "Search" in names
        assert "Panes" in names
        assert "General" in names


import pytest
from textual.widgets import Label
from toolong.help import ApertureHelpScreen
from toolong.config.schema import KeysConfig


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
