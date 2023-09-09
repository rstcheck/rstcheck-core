"""Integration test for the main runner."""
from __future__ import annotations

import io
import pathlib
import re
import sys

import pytest

from rstcheck_core import _extras, config, runner
from tests.conftest import EXAMPLES_DIR
from tests.integration_tests.conftest import ERROR_CODE_REGEX


class TestInput:
    """Test file input with good and bad files and piping."""

    @staticmethod
    @pytest.mark.parametrize("test_file", list(EXAMPLES_DIR.glob("good/*.rst")))
    def test_all_good_examples(test_file: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test all files in ``testing/examples/good`` are errorless."""
        if sys.platform == "win32" and test_file.name == "bom.rst":
            pytest.xfail(reason="BOM test fails for windows")
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    @pytest.mark.xfail(
        sys.platform == "win32", reason="Random unknown Windows specific wrong result", strict=False
    )
    def test_all_good_examples_recurively(capsys: pytest.CaptureFixture[str]) -> None:
        """Test all files in ``testing/examples/good`` recursively."""
        test_dir = EXAMPLES_DIR / "good"
        init_config = config.RstcheckConfig(recursive=True)
        _runner = runner.RstcheckMainRunner(check_paths=[test_dir], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    @pytest.mark.parametrize("test_file", list(EXAMPLES_DIR.glob("bad/*.rst")))
    def test_all_bad_examples(test_file: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test all files in ``testing/examples/bad`` have errors."""
        if sys.platform == "win32" and test_file.name == "bash.rst":
            pytest.xfail(reason="Unknown Windows specific wrong result for bash.rst")
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert ERROR_CODE_REGEX.search(capsys.readouterr().err) is not None

    @staticmethod
    def test_all_bad_examples_recurively(capsys: pytest.CaptureFixture[str]) -> None:
        """Test all files in ``testing/examples/bad`` recursively."""
        test_dir = EXAMPLES_DIR / "bad"
        init_config = config.RstcheckConfig(recursive=True)
        _runner = runner.RstcheckMainRunner(check_paths=[test_dir], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert ERROR_CODE_REGEX.search(capsys.readouterr().err) is not None

    @staticmethod
    def test_mix_of_good_and_bad_examples(capsys: pytest.CaptureFixture[str]) -> None:
        """Test mix of good and bad examples."""
        test_file_good = EXAMPLES_DIR / "good" / "rst.rst"
        test_file_bad = EXAMPLES_DIR / "bad" / "rst.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(
            check_paths=[test_file_good, test_file_bad], rstcheck_config=init_config
        )

        result = _runner.run()

        assert result != 0
        assert ERROR_CODE_REGEX.search(capsys.readouterr().err) is not None

    @staticmethod
    def test_good_example_with_piping(
        monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test good example file piped into rstcheck."""
        test_file_pipe = EXAMPLES_DIR / "good" / "rst.rst"
        test_file_pipe_content = test_file_pipe.read_text("utf-8")
        monkeypatch.setattr(sys, "stdin", io.StringIO(test_file_pipe_content))
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(
            check_paths=[pathlib.Path("-")], rstcheck_config=init_config
        )

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_bad_example_with_piping(
        monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test bad example file piped into rstcheck."""
        test_file_pipe = EXAMPLES_DIR / "bad" / "rst.rst"
        test_file_pipe_content = test_file_pipe.read_text("utf-8")
        monkeypatch.setattr(sys, "stdin", io.StringIO(test_file_pipe_content))
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(
            check_paths=[pathlib.Path("-")], rstcheck_config=init_config
        )

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 1

    @staticmethod
    def test_piping_with_additional_files_results_in_nonexisting_file(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test piping into rstcheck is ignored with additional files."""
        test_file = EXAMPLES_DIR / "good" / "rst.rst"
        test_file_pipe = EXAMPLES_DIR / "bad" / "rst.rst"
        test_file_pipe_content = test_file_pipe.read_text("utf-8")
        monkeypatch.setattr(sys, "stdin", io.StringIO(test_file_pipe_content))
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(
            check_paths=[pathlib.Path("-"), test_file], rstcheck_config=init_config
        )

        result = _runner.run()

        assert result != 0
        assert "Error! Issues detected." in capsys.readouterr().err
        assert "Path does not exist or is not a file: '-'." in caplog.text


class TestIgnoreOptions:
    """Test ignore_* options and report_level."""

    @staticmethod
    def test_without_report_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad example without report is ok."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"
        init_config = config.RstcheckConfig(report_level="none")
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_ignore_language_silences_error(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad example with ignored language is ok."""
        test_file = EXAMPLES_DIR / "bad" / "cpp.rst"
        init_config = config.RstcheckConfig(ignore_languages="cpp")
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_matching_ignore_msg_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
        """Test matching ignore message."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"
        init_config = config.RstcheckConfig(
            ignore_messages=r"(Title .verline & underline mismatch\.$)"
        )
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_non_matching_ignore_msg_errors(capsys: pytest.CaptureFixture[str]) -> None:
        """Test non matching ignore message."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"
        init_config = config.RstcheckConfig(ignore_messages=r"(No match\.$)")
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 1

    @staticmethod
    def test_table_substitution_error_fixed_by_ignore(capsys: pytest.CaptureFixture[str]) -> None:
        """Test that ignored substitutions in tables are correctly handled."""
        test_file = EXAMPLES_DIR / "bad" / "table_substitutions.rst"
        init_config = config.RstcheckConfig(ignore_substitutions="FOO_ID,BAR_ID")
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out


class TestWithoutConfigFile:
    """Test without config file in dir tree."""

    @staticmethod
    def test_error_without_config_file(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad example without set config file and implicit config file shows errors."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 6

    @staticmethod
    def test_no_error_with_set_ini_config_file(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad example with set INI config file does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_no_error_with_set_config_dir(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad example with set config dir does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_dir = EXAMPLES_DIR / "with_configuration"
        init_config = config.RstcheckConfig(config_path=config_dir)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    def test_no_error_with_set_toml_config_file(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad example with set TOML config file does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "pyproject.toml"
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out


class TestWithConfigFile:
    """Test with config file in dir tree."""

    @staticmethod
    def test_file_1_is_bad_without_config(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad file ``bad.rst`` without config file is not ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        config_file = pathlib.Path("NONE")
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 6

    @staticmethod
    def test_file_2_is_bad_without_config(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad file ``bad_rst.rst`` without config file not ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        config_file = pathlib.Path("NONE")
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 2

    @staticmethod
    def test_bad_file_1_with_implicit_config_no_errors(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad file ``bad.rst`` with implicit config file is ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_bad_file_2_with_implicit_config_some_errors(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test bad file ``bad_rst.rst`` with implicit config file partially ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 1

    @staticmethod
    def test_bad_file_1_with_explicit_config_no_errors(capsys: pytest.CaptureFixture[str]) -> None:
        """Test bad file ``bad.rst`` with explicit config file is ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_bad_file_2_with_explicit_config_some_errors(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test bad file ``bad_rst.rst`` with explicit config file partially ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 1


class TestWarningOnUnknownSettings:
    """Test warnings logged on unknown settings in config files."""

    @staticmethod
    @pytest.mark.parametrize("config_file_name", ["bad_config.cfg", "bad_config.toml"])
    def test_no_warnings_are_logged_by_default(
        config_file_name: str,
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that no warning is logged on unknown setting by default."""
        test_file = EXAMPLES_DIR / "good" / "rst.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / config_file_name
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out
        assert "Unknown setting(s)" not in caplog.text

    @staticmethod
    @pytest.mark.parametrize("config_file_name", ["bad_config.cfg", "bad_config.toml"])
    def test_no_warnings_are_logged_by_default_on_ini_files(
        config_file_name: str,
        caplog: pytest.LogCaptureFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test that a warning is logged on unknown setting when activated."""
        test_file = EXAMPLES_DIR / "good" / "rst.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / config_file_name
        init_config = config.RstcheckConfig(config_path=config_file, warn_unknown_settings=True)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out
        assert "Unknown setting(s)" in caplog.text


class TestCustomDirectivesAndRoles:
    """Test custom directives and roles."""

    @staticmethod
    def test_custom_directive_and_role(capsys: pytest.CaptureFixture[str]) -> None:
        """Test file with custom directive and role."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 4

    @staticmethod
    def test_custom_directive_and_role_with_ignore(capsys: pytest.CaptureFixture[str]) -> None:
        """Test file with custom directive and role and CLI ignores."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
        init_config = config.RstcheckConfig(
            ignore_directives="custom-directive", ignore_roles="custom-role"
        )
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_custom_directive_and_role_with_config_file(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test file with custom directive and role and config file."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
        config_file = EXAMPLES_DIR / "custom" / "rstcheck.custom.ini"
        init_config = config.RstcheckConfig(config_path=config_file)
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out


class TestSphinx:
    """Test integration with sphinx."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_sphinx_role_erros_without_sphinx(capsys: pytest.CaptureFixture[str]) -> None:
        """Test sphinx example errors without sphinx."""
        test_file = EXAMPLES_DIR / "sphinx" / "good.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(ERROR_CODE_REGEX.findall(capsys.readouterr().err)) == 2

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_sphinx_role_exits_zero_with_sphinx(capsys: pytest.CaptureFixture[str]) -> None:
        """Test sphinx example does not error with sphinx."""
        test_file = EXAMPLES_DIR / "sphinx" / "good.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out


class TestInlineIgnoreComments:
    """Test inline config comments to ignore things."""

    @staticmethod
    def test_bad_example_has_issues(capsys: pytest.CaptureFixture[str]) -> None:
        """Test all issues are found on bad example."""
        test_file = EXAMPLES_DIR / "inline_config" / "without_inline_ignore.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        stderr = capsys.readouterr().err
        assert len(ERROR_CODE_REGEX.findall(stderr)) == 6
        assert "custom-directive" in stderr
        assert "custom-role" in stderr
        assert "python" in stderr
        assert "unmatched-substitution" in stderr

    @staticmethod
    def test_bad_example_has_no_issues_with_inline_ignores(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test no issues are found on bad example with ignore comments."""
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_ignore.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result == 0
        assert "Success! No issues detected." in capsys.readouterr().out


class TestInlineFlowControlComments:
    """Test inline flow control comments to e.g. skip things."""

    @staticmethod
    @pytest.mark.skipif(sys.version_info[0:2] > (3, 9), reason="Requires python3.9 or lower")
    def test_bad_example_has_only_one_issue_pre310(capsys: pytest.CaptureFixture[str]) -> None:
        """Test only one issue is detected for two same code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(re.findall(r"unexpected EOF while parsing", capsys.readouterr().err)) == 1

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_bad_example_has_only_one_issue(capsys: pytest.CaptureFixture[str]) -> None:
        """Test only one issue is detected for two same code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(re.findall(r"'\(' was never closed", capsys.readouterr().err)) == 1

    @staticmethod
    @pytest.mark.skipif(sys.version_info[0:2] > (3, 9), reason="Requires python3.9 or lower")
    def test_nested_bad_example_has_only_one_issue_pre310(
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test only one issue is detected for two same nested code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_nested_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(re.findall(r"unexpected EOF while parsing", capsys.readouterr().err)) == 1

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_nested_bad_example_has_only_one_issue(capsys: pytest.CaptureFixture[str]) -> None:
        """Test only one issue is detected for two same nested code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_nested_inline_skip_code_block.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(check_paths=[test_file], rstcheck_config=init_config)

        result = _runner.run()

        assert result != 0
        assert len(re.findall(r"'\(' was never closed", capsys.readouterr().err)) == 1
