"""Tests for ``_sphinx`` module."""

from __future__ import annotations

import typing as t

import pytest

from rstcheck_core import _extras, _sphinx


class TestSphinxDirectiveAndRoleGetter:
    """Test ``get_sphinx_directives_and_roles`` function."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_exception_on_missing_sphinx() -> None:
        """Test that the install guard triggers."""
        with pytest.raises(ModuleNotFoundError):
            _sphinx.get_sphinx_directives_and_roles()

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_c_domain_is_loaded() -> None:
        """Test C domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "c:function" in result_directives
        assert "member" in result_roles
        assert "c:member" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_cpp_domain_is_loaded() -> None:
        """Test C++ domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "cpp:function" in result_directives
        assert "member" in result_roles
        assert "cpp:member" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_javascript_domain_is_loaded() -> None:
        """Test JavaScript domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "js:function" in result_directives
        assert "func" in result_roles
        assert "js:func" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_python_domain_is_loaded() -> None:
        """Test Python domain is loaded."""
        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "function" in result_directives
        assert "py:function" in result_directives
        assert "func" in result_roles
        assert "py:func" in result_roles

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_docutils_state_dict_is_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test docutils' state is loaded."""
        test_dict_directives: dict[str, t.Any] = {"test-directive": "test-directive"}
        monkeypatch.setattr("sphinx.util.docutils.directives._directives", test_dict_directives)
        test_dict_roles: dict[str, t.Any] = {"test-role": "test-role"}
        monkeypatch.setattr("sphinx.util.docutils.roles._roles", test_dict_roles)

        (result_directives, result_roles) = _sphinx.get_sphinx_directives_and_roles()  # act

        assert "test-directive" in result_directives
        assert "test-role" in result_roles


class TestDirectiveAndRoleFilter:
    """Test ``filter_whitelisted_directives_and_roles`` function."""

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_directives_are_filtered(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test directives are filtered."""
        monkeypatch.setattr(_sphinx, "_DIRECTIVE_WHITELIST", ["test-directive"])
        unfiltered_directives = ["test-directive", "test-directive2"]

        (result_directives, _) = _sphinx.filter_whitelisted_directives_and_roles(
            unfiltered_directives, []
        )  # act

        assert "test-directive" not in result_directives
        assert "test-directive2" in result_directives

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_code_directives_are_filtered() -> None:
        """Test code directives are filtered."""
        (unfiltered_directives, _) = _sphinx.get_sphinx_directives_and_roles()

        (result_directives, _) = _sphinx.filter_whitelisted_directives_and_roles(
            unfiltered_directives, []
        )  # act

        assert "code" not in result_directives
        assert "code-block" not in result_directives
        assert "sourcecode" not in result_directives

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_roles_are_filtered(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test roles are filtered."""
        monkeypatch.setattr(_sphinx, "_ROLE_WHITELIST", ["test-role"])
        unfiltered_roles = ["test-role", "test-role2"]

        (_, result_roles) = _sphinx.filter_whitelisted_directives_and_roles(
            [], unfiltered_roles
        )  # act

        assert "test-role" not in result_roles
        assert "test-role2" in result_roles
