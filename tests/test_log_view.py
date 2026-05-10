import pytest
from pathlib import Path
from unittest.mock import patch
from toolong.log_view import LogView
from toolong.log_lines import LogLines
from toolong.ui import UI


@pytest.fixture
async def log_view(tmp_path):
    """Start a headless UI with one log file and yield the LogView widget."""
    log_file = tmp_path / "test.log"
    log_file.write_text("line one\nline two\nline three\n", encoding="utf-8")

    app = UI(file_paths=[str(log_file)])
    async with app.run_test(headless=True) as pilot:
        await pilot.pause()
        await pilot.pause(0.1)  # allow Lazy-loaded LogView to mount
        view = app.screen.query_one(LogView)
        yield view


async def test_action_next_match_advances_search_forward(log_view):
    """action_next_match must call advance_search(+1), not advance_search(-1)."""
    with patch.object(log_view.query_one(LogLines), "advance_search") as mock_adv:
        log_view.action_next_match()
        mock_adv.assert_called_once_with(1)


async def test_action_prev_match_advances_search_backward(log_view):
    """action_prev_match must call advance_search(-1), not advance_search(+1)."""
    with patch.object(log_view.query_one(LogLines), "advance_search") as mock_adv:
        log_view.action_prev_match()
        mock_adv.assert_called_once_with(-1)


async def test_next_and_prev_match_use_opposite_signs(log_view):
    """Regression: next and prev must use opposite signs."""
    calls = []
    with patch.object(
        log_view.query_one(LogLines),
        "advance_search",
        side_effect=lambda n: calls.append(n),
    ):
        log_view.action_next_match()
        log_view.action_prev_match()

    assert len(calls) == 2
    assert calls[0] == 1, f"next_match should pass +1, got {calls[0]}"
    assert calls[1] == -1, f"prev_match should pass -1, got {calls[1]}"
    assert calls[0] != calls[1], "next and prev must use different signs"


import asyncio


async def test_split_mode_starts_as_none(log_view):
    """split_mode must be None on mount (panel hidden)."""
    assert log_view.split_mode is None


async def test_split_mode_none_removes_show_panel_class(log_view):
    """Setting split_mode to None must remove the show-panel CSS class."""
    log_view.split_mode = "vertical"
    await asyncio.sleep(0)
    log_view.split_mode = None
    await asyncio.sleep(0)
    assert not log_view.has_class("show-panel")


async def test_split_mode_vertical_adds_show_panel_class(log_view):
    """Setting split_mode to 'vertical' must add the show-panel CSS class."""
    log_view.split_mode = "vertical"
    await asyncio.sleep(0)
    assert log_view.has_class("show-panel")


async def test_split_mode_horizontal_adds_show_panel_class(log_view):
    """Setting split_mode to 'horizontal' must add the show-panel CSS class."""
    log_view.split_mode = "horizontal"
    await asyncio.sleep(0)
    assert log_view.has_class("show-panel")


async def test_split_mode_horizontal_sets_vertical_layout(log_view):
    """Horizontal split must switch LogView layout to 'vertical' so panel sits below."""
    log_view.split_mode = "horizontal"
    await asyncio.sleep(0)
    assert log_view.styles.layout.name == "vertical"


async def test_split_mode_vertical_keeps_horizontal_layout(log_view):
    """Vertical split must keep LogView layout as 'horizontal' (side by side)."""
    log_view.split_mode = "vertical"
    await asyncio.sleep(0)
    assert log_view.styles.layout.name == "horizontal"


async def test_split_mode_none_resets_layout_to_horizontal(log_view):
    """Closing panel must reset LogView layout to 'horizontal'."""
    log_view.split_mode = "horizontal"
    await asyncio.sleep(0)
    log_view.split_mode = None
    await asyncio.sleep(0)
    assert log_view.styles.layout.name == "horizontal"
