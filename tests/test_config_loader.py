from __future__ import annotations

from toolong.ui import CompareTokens


class TestCompareTokens:
    def test_eq_with_non_compare_tokens_returns_not_implemented(self):
        ct = CompareTokens("foo.log")
        result = ct.__eq__("some string")
        assert result is NotImplemented

    def test_eq_with_non_compare_tokens_does_not_raise(self):
        ct = CompareTokens("foo.log")
        assert ct != "some string"
        assert ct != 42
        assert ct != None  # noqa: E711
