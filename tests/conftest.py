"""Fixtures for tests."""
import typing as t

import docutils.parsers.rst
import pytest

from rstcheck_core import _extras


if _extras.SPHINX_INSTALLED:
    import sphinx.application


@pytest.fixture(name="patch_docutils_directives_and_roles_dict")
def _patch_docutils_directives_and_roles_dict_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monkeypatch docutils' directives and roles state dicts.

    This patch is required when tests are run in parallel (default), because they would
    under the hood all write to the same state dicts otherwise and influence each other.
    """
    test_dict_directives: t.Dict[str, t.Any] = {}
    test_dict_roles: t.Dict[str, t.Any] = {}

    if _extras.SPHINX_INSTALLED:
        monkeypatch.setattr(
            sphinx.application.docutils.directives, "_directives", test_dict_directives
        )
        monkeypatch.setattr(sphinx.application.docutils.roles, "_roles", test_dict_roles)
    else:
        monkeypatch.setattr(docutils.parsers.rst.directives, "_directives", test_dict_directives)
        monkeypatch.setattr(docutils.parsers.rst.roles, "_roles", test_dict_roles)
