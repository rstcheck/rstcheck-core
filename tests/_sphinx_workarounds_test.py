"""Tests for ``_sphinx_workarounds`` module."""

from __future__ import annotations

import pathlib
import re

import pytest

from rstcheck_core import _extras, _sphinx_workarounds


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_yield_include_errors_no_errors(tmp_path: pathlib.Path) -> None:
    """Test include directive yields no errors when file exists."""
    include_file = "exists.rst"
    (tmp_path / include_file).write_text("Hello\n")
    source = f".. include:: {include_file}"

    result = list(
        _sphinx_workarounds.yield_include_errors(source, source_origin=tmp_path / "test.rst")
    )

    assert not result


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_yield_include_errors_missing_file() -> None:
    """Test include directive referencing non-existent file yields an error."""
    source = ".. include:: does_not_exist.rst"

    result = list(
        _sphinx_workarounds.yield_include_errors(source, source_origin=pathlib.Path("test.rst"))
    )

    assert len(result) == 1
    assert result[0]["line_number"] == 1
    assert 'File referenced in "include" directive not found:' in result[0]["message"]
    assert "does_not_exist.rst" in result[0]["message"]


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_strip_include_directives_no_options() -> None:
    """Test include directive without options is stripped."""
    source = """
Some text before.

.. include:: somefile.rst

Some text after.
"""
    result = _sphinx_workarounds.strip_include_directives(source)

    assert result == "\nSome text before.\n\n\n\nSome text after.\n"


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_strip_include_directives_with_options() -> None:
    """Test include directive with options is stripped correctly and line count is preserved."""
    source = """
Some text before.

.. include:: somefile.rst
   :start-line: 1
   :end-line: 10

Some text after.
"""
    result = _sphinx_workarounds.strip_include_directives(source)

    assert result == "\nSome text before.\n\n\n\n\n\nSome text after.\n"


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_strip_include_directives_with_other_content() -> None:
    """Test with other indented content after."""
    source = """
  .. include:: somefile.rst
     :start-line: 1
     :end-line: 10

  Some blockquote after.
"""
    result = _sphinx_workarounds.strip_include_directives(source)

    assert result == "\n\n\n\n\n  Some blockquote after.\n"


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_strip_include_directives_with_unindented_field_list() -> None:
    """Test include directive does not swallow trailing field list."""
    source = """
Bla.

.. include:: other_file.rst

:hello: this is not an include option

Another paragraph.
"""
    result = _sphinx_workarounds.strip_include_directives(source)

    assert result == "\nBla.\n\n\n\n:hello: this is not an include option\n\nAnother paragraph.\n"


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_strip_include_directives_with_indented_unrelated_content() -> None:
    """Test indented include directive doesn't swallow unrelated same-level indented content."""
    source = """
Some text before.

.. rst-class:: my-class

    .. include:: other_file.txt

    :hello: this is not an include option

Some text after.
"""
    result = _sphinx_workarounds.strip_include_directives(source)

    assert (
        result
        == "\nSome text before.\n\n.. rst-class:: my-class\n\n\n\n    :hello: this is not an include option\n\nSome text after.\n"
    )


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_changing_line_numbers_for_error_cases() -> None:
    """Check that line numbers for errors match the source BEFORE AND AFTER stripping happens."""
    source = """
Some text.

.. include:: does_not_exist.rst
   :start-line: 1

.. include:: does_not_exist_either.rst
"""

    errors = list(
        _sphinx_workarounds.yield_include_errors(source, source_origin=pathlib.Path("test.rst"))
    )

    assert len(errors) == 2
    assert errors[0]["line_number"] == 4
    assert errors[1]["line_number"] == 7

    stripped_source = _sphinx_workarounds.strip_include_directives(source)

    assert stripped_source.count("\n") == source.count("\n")
    assert stripped_source == "\nSome text.\n\n\n\n\n\n"


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_yield_include_errors_with_ignore_messages() -> None:
    """Test include directive respects ignore_messages."""
    source = ".. include:: does_not_exist.rst"

    ignore_pattern = re.compile(r"File referenced in \"include\" directive not found")

    result = list(
        _sphinx_workarounds.yield_include_errors(
            source, source_origin=pathlib.Path("test.rst"), ignore_messages=ignore_pattern
        )
    )

    assert not result


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_yield_include_errors_abs_path_with_source_dir_auto_discovery_failing() -> None:
    """Test source dir auto-discovery failing for included absolute path file."""
    source = ".. include:: /absolute.rst"

    result = list(
        _sphinx_workarounds.yield_include_errors(source, source_origin=pathlib.Path("test.rst"))
    )

    assert len(result) == 1
    assert result[0]["line_number"] == 1
    assert 'File referenced in "include" directive not found:' in result[0]["message"]
    assert "Could not find sphinx 'source' directory" in result[0]["message"]


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_yield_include_errors_abs_path_with_source_dir_auto_discovery_working(
    tmp_path: pathlib.Path,
) -> None:
    """Test source dir auto-discovery working for included absolute path file."""
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    include_file = source_dir / "absolute.rst"
    include_file.write_text("Hello\n")
    source = ".. include:: /absolute.rst"

    result = list(
        _sphinx_workarounds.yield_include_errors(source, source_origin=source_dir / "test.rst")
    )

    assert not result


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_yield_include_errors_abs_path_with_passed_sphinx_source_dir(
    tmp_path: pathlib.Path,
) -> None:
    """Test source dir auto-discovery working for included absolute path file."""
    source_dir = tmp_path / "source"
    source_dir.mkdir(parents=True)
    include_file = source_dir / "absolute.rst"
    include_file.write_text("Hello\n")
    source = ".. include:: /absolute.rst"

    result = list(
        _sphinx_workarounds.yield_include_errors(
            source, source_origin=pathlib.Path("test.rst"), sphinx_source_dir=source_dir
        )
    )

    assert not result
