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
    sphinx_source_dir: pathlib.Path | None = None,
) -> types.YieldedLintError:
    """Check existence of included files from include directives.

    :param source: Source containing include directives
    :param source_origin: Origin of the source
    :param ignore_messages: Regex for ignoring error messages; defaults to :py:obj:`None`
    :return: :py:obj:`None`
    :yield: Found issues
    """
    if isinstance(source_origin, pathlib.Path) and source_origin.name != "-":
        base_dir = source_origin.parent.absolute()
    else:
        base_dir = pathlib.Path.cwd().absolute()

    for match in _INCLUDE_REGEX.finditer(source):
        line_number = source[: match.start()].count("\n") + 1
        include_file_path_raw = match.group(2).strip()
        include_file_path = pathlib.Path(include_file_path_raw)

        base_err_message = '(SEVERE/4) File referenced in "include" directive not found:'

        if not include_file_path_raw.startswith("/"):
            include_file_path = base_dir / include_file_path
        elif sphinx_source_dir is not None:
            include_file_path = sphinx_source_dir.absolute() / include_file_path_raw.lstrip("/")
        else:
            found_source_dir = base_dir
            while len(found_source_dir.parents) > 0:
                if found_source_dir.stem == "source":
                    break
                found_source_dir = found_source_dir.parent
            else:
                message = base_err_message + (
                    " Could not find sphinx 'source' directory. Please provide via config."
                )
                yield types.LintError(
                    source_origin=source_origin, line_number=line_number, message=message
                )
                continue
            include_file_path = found_source_dir / include_file_path_raw.lstrip("/")

        if not include_file_path.is_file():
            line_number = source[: match.start()].count("\n") + 1
            message = f"{base_err_message} '{include_file_path}'."

            if ignore_messages and ignore_messages.search(message):
                continue

            yield types.LintError(
                source_origin=source_origin, line_number=line_number, message=message
            )
