"""Compatability code for older python version."""
from __future__ import annotations

try:
    from importlib.metadata import version
except ImportError:  # pragma: py-gte-38
    from importlib_metadata import version  # type: ignore[import,no-redef]

try:
    from typing import Protocol
except ImportError:  # pragma: py-gte-38
    from typing_extensions import Protocol  # type: ignore[assignment]

try:
    from typing import TypedDict
except ImportError:  # pragma: py-gte-38
    from typing_extensions import TypedDict


__all__ = ["Protocol", "TypedDict", "version"]
