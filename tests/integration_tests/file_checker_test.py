"""Integration test for the main runner."""
from __future__ import annotations

import io
import pathlib
import re
import sys
import typing as t

import pytest

from rstcheck_core import _extras, checker, config
from tests.conftest import EXAMPLES_DIR


class TestInput:
    """Test file input with good and bad files and piping."""

    @staticmethod
    @pytest.mark.parametrize("test_file", list(EXAMPLES_DIR.glob("good/*.rst")))
    def test_all_good_examples(test_file: pathlib.Path) -> None:
        """Test all files in ``testing/examples/good`` are errorless."""
        if sys.platform == "win32" and test_file.name == "bom.rst":
            pytest.xfail(reason="BOM test fails for windows")
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    @pytest.mark.parametrize("test_file", list(EXAMPLES_DIR.glob("bad/*.rst")))
    def test_all_bad_examples(test_file: pathlib.Path) -> None:
        """Test all files in ``testing/examples/bad`` have errors."""
        if sys.platform == "win32" and test_file.name == "bash.rst":
            pytest.xfail(reason="Unknown Windows specific wrong result for bash.rst")
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) > 0

    @staticmethod
    def test_good_example_with_piping(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test good example file piped into rstcheck."""
        test_file_pipe = EXAMPLES_DIR / "good" / "rst.rst"
        test_file_pipe_content = test_file_pipe.read_text("utf-8")
        monkeypatch.setattr(sys, "stdin", io.StringIO(test_file_pipe_content))
        init_config = config.RstcheckConfig()

        result = checker.check_file(pathlib.Path("-"), init_config)

        assert not result

    @staticmethod
    def test_bad_example_with_piping(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test bad example file piped into rstcheck."""
        test_file_pipe = EXAMPLES_DIR / "bad" / "rst.rst"
        test_file_pipe_content = test_file_pipe.read_text("utf-8")
        monkeypatch.setattr(sys, "stdin", io.StringIO(test_file_pipe_content))
        init_config = config.RstcheckConfig()

        result = checker.check_file(pathlib.Path("-"), init_config)

        assert len(result) == 1


class TestIgnoreOptions:
    """Test ignore_* options and report_level."""

    @staticmethod
    def test_without_report_exits_zero() -> None:
        """Test bad example without report is ok."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"
        init_config = config.RstcheckConfig(report_level="none")

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    def test_ignore_language_silences_error() -> None:
        """Test bad example with ignored language is ok."""
        test_file = EXAMPLES_DIR / "bad" / "cpp.rst"
        init_config = config.RstcheckConfig(ignore_languages="cpp")

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    def test_matching_ignore_msg_exits_zero() -> None:
        """Test matching ignore message."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"
        init_config = config.RstcheckConfig(
            ignore_messages=r"(Title .verline & underline mismatch\.$)"
        )

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    def test_non_matching_ignore_msg_errors() -> None:
        """Test non matching ignore message."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"
        init_config = config.RstcheckConfig(ignore_messages=r"(No match\.$)")

        result = checker.check_file(test_file, init_config)

        assert len(result) == 1

    @staticmethod
    def test_table_substitution_error_fixed_by_ignore() -> None:
        """Test that ignored substitutions in tables are correctly handled."""
        test_file = EXAMPLES_DIR / "bad" / "table_substitutions.rst"
        init_config = config.RstcheckConfig(ignore_substitutions="FOO_ID,BAR_ID")

        result = checker.check_file(test_file, init_config)

        assert not result


class TestWithoutConfigFile:
    """Test without config file in dir tree."""

    @staticmethod
    def test_error_without_config_file() -> None:
        """Test bad example without set config file and implicit config file shows errors."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 6

    @staticmethod
    def test_no_error_with_set_ini_config_file() -> None:
        """Test bad example with set INI config file does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"
        file_config = t.cast(config.RstcheckConfigFile, config.load_config_file(config_file))
        init_config = config.RstcheckConfig(config_path=config_file, **file_config.model_dump())

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    def test_no_error_with_set_config_dir() -> None:
        """Test bad example with set config dir does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_dir = EXAMPLES_DIR / "with_configuration"
        file_config = t.cast(
            config.RstcheckConfigFile, config.load_config_file_from_dir(config_dir)
        )
        init_config = config.RstcheckConfig(config_path=config_dir, **file_config.model_dump())

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    def test_no_error_with_set_toml_config_file() -> None:
        """Test bad example with set TOML config file does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "pyproject.toml"
        file_config = t.cast(config.RstcheckConfigFile, config.load_config_file(config_file))
        init_config = config.RstcheckConfig(config_path=config_file, **file_config.model_dump())

        result = checker.check_file(test_file, init_config)

        assert not result


class TestWithConfigFile:
    """Test with config file in dir tree."""

    @staticmethod
    def test_file_1_is_bad_without_config() -> None:
        """Test bad file ``bad.rst`` without config file is not ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        init_config = config.RstcheckConfig(config_path=pathlib.Path("NONE"))

        result = checker.check_file(test_file, init_config)

        assert len(result) == 6

    @staticmethod
    def test_file_2_is_bad_without_config() -> None:
        """Test bad file ``bad_rst.rst`` without config file not ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        init_config = config.RstcheckConfig(config_path=pathlib.Path("NONE"))

        result = checker.check_file(test_file, init_config)

        assert len(result) == 2

    @staticmethod
    def test_bad_file_1_with_implicit_config_no_errors() -> None:
        """Test bad file ``bad.rst`` with implicit config file is ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    def test_bad_file_2_with_implicit_config_some_errors() -> None:
        """Test bad file ``bad_rst.rst`` with implicit config file partially ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 1

    @staticmethod
    def test_bad_file_1_with_explicit_config_no_errors() -> None:
        """Test bad file ``bad.rst`` with explicit config file is ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"
        file_config = t.cast(config.RstcheckConfigFile, config.load_config_file(config_file))
        init_config = config.RstcheckConfig(config_path=config_file, **file_config.model_dump())

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    def test_bad_file_2_with_explicit_config_some_errors() -> None:
        """Test bad file ``bad_rst.rst`` with explicit config file partially ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"
        file_config = t.cast(config.RstcheckConfigFile, config.load_config_file(config_file))
        init_config = config.RstcheckConfig(config_path=config_file, **file_config.model_dump())

        result = checker.check_file(test_file, init_config)

        assert len(result) == 1


class TestCustomDirectivesAndRoles:
    """Test custom directives and roles."""

    @staticmethod
    def test_custom_directive_and_role() -> None:
        """Test file with custom directive and role."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 4

    @staticmethod
    def test_custom_directive_and_role_with_ignore() -> None:
        """Test file with custom directive and role and CLI ignores."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
        init_config = config.RstcheckConfig(
            ignore_directives="custom-directive", ignore_roles="custom-role"
        )

        result = checker.check_file(test_file, init_config)

        assert not result

    @staticmethod
    def test_custom_directive_and_role_with_config_file() -> None:
        """Test file with custom directive and role and config file."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
        config_file = EXAMPLES_DIR / "custom" / "rstcheck.custom.ini"
        file_config = t.cast(config.RstcheckConfigFile, config.load_config_file(config_file))
        init_config = config.RstcheckConfig(config_path=config_file, **file_config.model_dump())

        result = checker.check_file(test_file, init_config)

        assert not result


class TestSphinx:
    """Test integration with sphinx."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_sphinx_role_erros_without_sphinx() -> None:
        """Test sphinx example errors without sphinx."""
        test_file = EXAMPLES_DIR / "sphinx" / "good.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 2

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_sphinx_role_exits_zero_with_sphinx() -> None:
        """Test sphinx example does not error with sphinx."""
        test_file = EXAMPLES_DIR / "sphinx" / "good.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert not result


class TestInlineIgnoreComments:
    """Test inline config comments to ignore things."""

    @staticmethod
    def test_bad_example_has_issues() -> None:
        """Test all issues are found on bad example."""
        test_file = EXAMPLES_DIR / "inline_config" / "without_inline_ignore.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 6
        err_msgs = "  ".join([e["message"] for e in result])
        assert "custom-directive" in err_msgs
        assert "custom-role" in err_msgs
        assert "python" in err_msgs
        assert "unmatched-substitution" in err_msgs

    @staticmethod
    def test_bad_example_has_no_issues_with_inline_ignores() -> None:
        """Test no issues are found on bad example with ignore comments."""
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_ignore.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert not result


class TestInlineFlowControlComments:
    """Test inline flow control comments to e.g. skip things."""

    @staticmethod
    @pytest.mark.skipif(sys.version_info[0:2] > (3, 9), reason="Requires python3.9 or lower")
    def test_bad_example_has_only_one_issue_pre310() -> None:
        """Test only one issue is detected for two same code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 1
        err_msgs = "  ".join([e["message"] for e in result])
        assert len(re.findall(r"unexpected EOF while parsing", err_msgs)) == 1

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_bad_example_has_only_one_issue() -> None:
        """Test only one issue is detected for two same code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 1
        err_msgs = "  ".join([e["message"] for e in result])
        assert len(re.findall(r"'\(' was never closed", err_msgs)) == 1

    @staticmethod
    @pytest.mark.skipif(sys.version_info[0:2] > (3, 9), reason="Requires python3.9 or lower")
    def test_nested_bad_example_has_only_one_issue_pre310() -> None:
        """Test only one issue is detected for two same nested code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_nested_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 1
        err_msgs = "  ".join([e["message"] for e in result])
        assert len(re.findall(r"unexpected EOF while parsing", err_msgs)) == 1

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_nested_bad_example_has_only_one_issue() -> None:
        """Test only one issue is detected for two same nested code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_nested_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()

        result = checker.check_file(test_file, init_config)

        assert len(result) == 1
        err_msgs = "  ".join([e["message"] for e in result])
        assert len(re.findall(r"'\(' was never closed", err_msgs)) == 1
