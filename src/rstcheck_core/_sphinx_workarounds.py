"""Sphinx workarounds for rstcheck."""

from __future__ import annotations

import pathlib
import re
import typing as t

from . import types

_INCLUDE_REGEX = re.compile(
    r"^([ \t]*)\.\.[ \t]+include::[ \t]+([^\n]+)(?:\n(?:[ \t]*$|\1[ \t]+(?:.*)))*",
    flags=re.MULTILINE,
)


def strip_include_directives(source: str) -> str:
    """Strip include directives from source to prevent Sphinx AttributeError.

    Replaces the directive and its options with newlines to preserve line numbers.

    :param source: Source to remove include directives from
    :return: Cleaned source
    """

    def replacer(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    return _INCLUDE_REGEX.sub(replacer, source)


def yield_include_errors(
    source: str,
    source_origin: types.SourceFileOrString,
    ignore_messages: t.Pattern[str] | None = None,
) -> types.YieldedLintError:
    """Check existence of included files from include directives.

    :param source: Source containing include directives
    :param source_origin: Origin of the source
    :param ignore_messages: Regex for ignoring error messages; defaults to :py:obj:`None`
    :return: :py:obj:`None`
    :yield: Found issues
    """
    if isinstance(source_origin, pathlib.Path) and source_origin.name != "-":
        base_dir = source_origin.parent
    else:
        base_dir = pathlib.Path.cwd()

    for match in _INCLUDE_REGEX.finditer(source):
        file_path_str = match.group(2).strip()

        target_path = pathlib.Path(file_path_str)
        if not target_path.is_absolute() and not (
            file_path_str.startswith("<") and file_path_str.endswith(">")
        ):
            target_path = base_dir / target_path

        if (
            not (file_path_str.startswith("<") and file_path_str.endswith(">"))
            and not target_path.is_file()
        ):
            line_number = source[: match.start()].count("\n") + 1
            message = (
                f"(SEVERE/4) File referenced in \"include\" directive not found: '{file_path_str}'."
            )

            if ignore_messages and ignore_messages.search(message):
                continue

            yield types.LintError(
                source_origin=source_origin, line_number=line_number, message=message
            )
