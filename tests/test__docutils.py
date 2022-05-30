"""Tests for ``_docutils`` module."""
# pylint: disable=protected-access
import typing as t

import docutils.parsers.rst.directives as docutils_directives
import docutils.parsers.rst.roles as docutils_roles
import pytest

from rstcheck_core import _docutils


class TestIgnoreDirectivesAndRoles:
    """Test ``ignore_directives_and_roles`` function."""

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_empty_lists() -> None:
        """Test with empty lists."""
        directives: t.List[str] = []
        roles: t.List[str] = []

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert not docutils_directives._directives
        assert not docutils_roles._roles

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_only_roles() -> None:
        """Test with only roles to add."""
        directives: t.List[str] = []
        roles = ["test_role"]

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert not docutils_directives._directives
        assert "test_role" in docutils_roles._roles

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_only_directives() -> None:
        """Test with only directives to add."""
        directives = ["test_directive"]
        roles: t.List[str] = []

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert "test_directive" in docutils_directives._directives
        assert not docutils_roles._roles

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_with_both() -> None:
        """Test with both."""
        directives = ["test_directive"]
        roles = ["test_role"]

        _docutils.ignore_directives_and_roles(directives, roles)  # act

        assert "test_directive" in docutils_directives._directives
        assert "test_role" in docutils_roles._roles


class TestRegisterCodeDirective:
    """Test ``register_code_directives`` function."""

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_registers_none_by_default() -> None:
        """Test function registers none directive by default."""
        _docutils.register_code_directives()  # act

        assert "code" not in docutils_directives._directives
        assert "code-block" not in docutils_directives._directives
        assert "sourcecode" not in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_does_nothing_and_all_ignored() -> None:
        """Test function does nothing when all ignores are ``True``."""
        _docutils.register_code_directives(  # act
            code_directive=_docutils.CodeBlockDirective,
            codeblock_directive=_docutils.CodeBlockDirective,
            sourcecode_directive=_docutils.CodeBlockDirective,
        )

        assert "code" in docutils_directives._directives
        assert "code-block" in docutils_directives._directives
        assert "sourcecode" in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_code_when_others_are_not_set() -> None:
        """Test function installes only code directive when others are not set."""
        _docutils.register_code_directives(  # act
            code_directive=_docutils.CodeBlockDirective,
        )

        assert "code" in docutils_directives._directives
        assert "code-block" not in docutils_directives._directives
        assert "sourcecode" not in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_code_block_when_others_are_not_set() -> None:
        """Test function installes only code-block directive when others are not set."""
        _docutils.register_code_directives(  # act
            codeblock_directive=_docutils.CodeBlockDirective,
        )

        assert "code" not in docutils_directives._directives
        assert "code-block" in docutils_directives._directives
        assert "sourcecode" not in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_sourcecode_when_others_are_not_set() -> None:
        """Test function installes only sourcecode directive when others are not set."""
        _docutils.register_code_directives(  # act
            sourcecode_directive=_docutils.CodeBlockDirective,
        )

        assert "code" not in docutils_directives._directives
        assert "code-block" not in docutils_directives._directives
        assert "sourcecode" in docutils_directives._directives


class TestRegisterRstcheckCodeDirectives:
    """Test ``register_rstcheck_code_directives`` function."""

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_registers_all() -> None:
        """Test function registers all directives."""
        _docutils.register_rstcheck_code_directives()  # act

        assert "code" in docutils_directives._directives
        assert "code-block" in docutils_directives._directives
        assert "sourcecode" in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_does_nothing_and_all_ignored() -> None:
        """Test function does nothing when all ignores are ``True``."""
        _docutils.register_rstcheck_code_directives(  # act
            ignore_code_directive=True,
            ignore_codeblock_directive=True,
            ignore_sourcecode_directive=True,
        )

        assert "code" not in docutils_directives._directives
        assert "code-block" not in docutils_directives._directives
        assert "sourcecode" not in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_code_when_others_are_ignored() -> None:
        """Test function installes only code directive when others are ignored."""
        _docutils.register_rstcheck_code_directives(  # act
            ignore_codeblock_directive=True, ignore_sourcecode_directive=True
        )

        assert "code" in docutils_directives._directives
        assert "code-block" not in docutils_directives._directives
        assert "sourcecode" not in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_code_block_when_others_are_ignored() -> None:
        """Test function installes only code-block directive when others are ignored."""
        _docutils.register_rstcheck_code_directives(  # act
            ignore_code_directive=True, ignore_sourcecode_directive=True
        )

        assert "code" not in docutils_directives._directives
        assert "code-block" in docutils_directives._directives
        assert "sourcecode" not in docutils_directives._directives

    @staticmethod
    @pytest.mark.usefixtures("patch_docutils_directives_and_roles_dict")
    def test_install_only_sourcecode_when_others_are_ignored() -> None:
        """Test function installes only sourcecode directive when others are ignored."""
        _docutils.register_rstcheck_code_directives(  # act
            ignore_code_directive=True, ignore_codeblock_directive=True
        )

        assert "code" not in docutils_directives._directives
        assert "code-block" not in docutils_directives._directives
        assert "sourcecode" in docutils_directives._directives
