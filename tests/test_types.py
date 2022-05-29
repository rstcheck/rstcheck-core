"""Tests for ``types`` module."""
import re

from rstcheck_core import types


class TestIgnoreDictConstructor:
    """Test ``construct_ignore_dict`` function."""

    @staticmethod
    def test_no_args() -> None:
        """Test construction of IgnoreDict with default values."""
        result = types.construct_ignore_dict()

        assert result == types.IgnoreDict(
            messages=None,
            languages=[],
            directives=[],
            roles=[],
            substitutions=[],
        )

    @staticmethod
    def test_all_args() -> None:
        """Test construction of IgnoreDict with set values."""
        result = types.construct_ignore_dict(
            messages=re.compile("msg"),
            languages=["lang"],
            directives=["dir"],
            roles=["role"],
            substitutions=["sub"],
        )

        assert result == types.IgnoreDict(
            messages=re.compile("msg"),
            languages=["lang"],
            directives=["dir"],
            roles=["role"],
            substitutions=["sub"],
        )
