"""Tests for ``config`` module."""

from __future__ import annotations

import logging
import pathlib
import re
import typing as t

import pytest

from rstcheck_core import _extras, config


def test_report_level_map_matches_numbers() -> None:
    """Test that the enum's values match the map's ones."""
    enum_values = [e.value for e in config.ReportLevel]
    map_values = list(config.ReportLevelMap.values())

    assert map_values == enum_values


def test_report_level_map_matches_names() -> None:
    """Test that the enum's name match the map's keys."""
    enum_names = [e.casefold() for e in config.ReportLevel._member_names_]
    map_keys = list(config.ReportLevelMap.keys())

    assert enum_names == map_keys


def test_default_values_for_config_file() -> None:
    """Test default values of ``RstcheckConfigFile``."""
    result = config.RstcheckConfigFile()

    assert result.report_level is None
    assert result.ignore_directives is None
    assert result.ignore_roles is None
    assert result.ignore_substitutions is None
    assert result.ignore_languages is None
    assert result.ignore_messages is None
    assert result.add_directives is None


def test_default_values_for_config() -> None:
    """Test default values of ``RstcheckConfig``."""
    result = config.RstcheckConfig()

    assert result.report_level is None
    assert result.ignore_directives is None  # type: ignore[unreachable]
    assert result.ignore_roles is None
    assert result.ignore_substitutions is None
    assert result.ignore_languages is None
    assert result.ignore_messages is None
    assert result.config_path is None
    assert result.recursive is None
    assert result.add_directives is None


class TestSplitStrValidator:
    """Test ``_split_str_validator`` validator function."""

    @staticmethod
    def test_none_means_default() -> None:
        """Test ``None`` results in ``None``."""
        result = config._split_str_validator(None)

        assert result is None

    @staticmethod
    @pytest.mark.parametrize(
        ("string", "split_list"),
        [
            ("value1", ["value1"]),
            ("value1,value2", ["value1", "value2"]),
            ("value1, value2", ["value1", "value2"]),
            ("value1 ,value2", ["value1", "value2"]),
            ("value1 , value2", ["value1", "value2"]),
            ("value1 ,\n value2", ["value1", "value2"]),
            ("value1 ,\n value2\n", ["value1", "value2"]),
            ("value1 , value2,", ["value1", "value2"]),
            ("value1 , value2 ,", ["value1", "value2"]),
            ("value1 , value2 , ", ["value1", "value2"]),
        ],
    )
    def test_strings_are_transformed_to_lists(string: str, split_list: list[str]) -> None:
        """Test strings are split at the ",", trailing commas are ignored and whitespace cleaned."""
        result = config._split_str_validator(string)

        assert result == split_list

    @staticmethod
    @pytest.mark.parametrize(
        ("string_list", "string_list_cleaned"),
        [
            (["value1"], ["value1"]),
            (["value1", "value2"], ["value1", "value2"]),
            (["value1", " value2"], ["value1", "value2"]),
            (["value1 ", "value2"], ["value1", "value2"]),
            (["value1 ", " value2"], ["value1", "value2"]),
        ],
    )
    def test_string_lists_are_whitespace_cleaned(
        string_list: list[str], string_list_cleaned: list[str]
    ) -> None:
        """Test lists of strings are whitespace cleaned."""
        result = config._split_str_validator(string_list)

        assert result == string_list_cleaned

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            1,
            [1],
            1.1,
            [1.1],
            False,
            [False],
            True,
            [True],
            ["foo", 1],
        ],
    )
    def test_invalid_settings(value: str) -> None:
        """Test invalid settings."""
        with pytest.raises(TypeError, match="^Not a string or list of strings$"):
            config._split_str_validator(value)


class TestReportLevelValidatorMethod:
    """Test ``valid_report_level`` validator method of the ``RstcheckConfig`` class.

    It validates the ``report_level`` setting.
    """

    @staticmethod
    def test_none_means_none() -> None:
        """Test ``None`` results in no report level."""
        result = config.RstcheckConfigFile(report_level=None)

        assert result is not None
        assert result.report_level is None

    @staticmethod
    def test_set_level_stays() -> None:
        """Test set level results in same level."""
        result = config.RstcheckConfigFile(report_level=config.ReportLevel.SEVERE)

        assert result is not None
        assert result.report_level is config.ReportLevel.SEVERE

    @staticmethod
    def test_empty_string_means_default() -> None:
        """Test empty string results in default report level."""
        result = config.RstcheckConfigFile(report_level="")

        assert result is not None
        assert result.report_level is config.ReportLevel.INFO

    @staticmethod
    @pytest.mark.parametrize(
        "level",
        [1, 2, 3, 4, 5, "info", "warning", "error", "severe", "none", "NONE", "None", "NoNe"],
    )
    def test_valid_report_levels(level: t.Any) -> None:  # noqa: ANN401
        """Test valid report levels accepted by docutils."""
        result = config.RstcheckConfigFile(report_level=level)

        assert result is not None
        assert result.report_level is not None

    @staticmethod
    @pytest.mark.parametrize(
        "level",
        [-1, 0, 1.5, 6, 32, False, True, "information", "warn", "err", "critical", "fatal"],
    )
    def test_invalid_report_levels(level: t.Any) -> None:  # noqa: ANN401
        """Test invalid report levels not accepted by docutils."""
        with pytest.raises(TypeError, match="^Invalid report level$"):
            config.RstcheckConfigFile(report_level=level)


class TestSplitStrValidatorMethod:
    """Test ``split_str`` validator method of the ``RstcheckConfig`` class.

    It validates the

    - ``ignore_directives``
    - ``ignore_roles``
    - ``ignore_substitutions``
    - ``ignore_languages``
    - ``add_directives``

    settings.
    """

    @staticmethod
    def test_none_means_default() -> None:
        """Test ``None`` results in unset ignore_messages."""
        result = config.RstcheckConfigFile(
            ignore_languages=None,
            ignore_directives=None,
            ignore_roles=None,
            ignore_substitutions=None,
            add_directives=None,
        )

        assert result is not None
        assert result.ignore_languages is None
        assert result.ignore_directives is None
        assert result.ignore_roles is None
        assert result.ignore_substitutions is None
        assert result.add_directives is None

    @staticmethod
    @pytest.mark.parametrize(
        ("string", "split_list"),
        [
            ("value1", ["value1"]),
            ("value1,value2", ["value1", "value2"]),
            ("value1, value2", ["value1", "value2"]),
            ("value1 ,value2", ["value1", "value2"]),
            ("value1 , value2", ["value1", "value2"]),
            ("value1 ,\n value2", ["value1", "value2"]),
            ("value1 ,\n value2\n", ["value1", "value2"]),
            ("value1 , value2,", ["value1", "value2"]),
            ("value1 , value2 ,", ["value1", "value2"]),
            ("value1 , value2 , ", ["value1", "value2"]),
        ],
    )
    def test_strings_are_transformed_to_lists(string: str, split_list: list[str]) -> None:
        """Test strings are split at the ",", trailing commas are ignored and whitespace cleaned."""
        result = config.RstcheckConfigFile(
            ignore_languages=string,
            ignore_directives=string,
            ignore_roles=string,
            ignore_substitutions=string,
            add_directives=string,
        )

        assert result is not None
        assert result.ignore_languages == split_list
        assert result.ignore_directives == split_list
        assert result.ignore_roles == split_list
        assert result.ignore_substitutions == split_list
        assert result.add_directives == split_list

    @staticmethod
    @pytest.mark.parametrize(
        ("string_list", "string_list_cleaned"),
        [
            (["value1"], ["value1"]),
            (["value1", "value2"], ["value1", "value2"]),
            (["value1", " value2"], ["value1", "value2"]),
            (["value1 ", "value2"], ["value1", "value2"]),
            (["value1 ", " value2"], ["value1", "value2"]),
        ],
    )
    def test_string_lists_are_whitespace_cleaned(
        string_list: list[str], string_list_cleaned: list[str]
    ) -> None:
        """Test lists of strings are whitespace cleaned."""
        result = config.RstcheckConfigFile(
            ignore_languages=string_list,
            ignore_directives=string_list,
            ignore_roles=string_list,
            ignore_substitutions=string_list,
            add_directives=string_list,
        )

        assert result is not None
        assert result.ignore_languages == string_list_cleaned
        assert result.ignore_directives == string_list_cleaned
        assert result.ignore_roles == string_list_cleaned
        assert result.ignore_substitutions == string_list_cleaned
        assert result.add_directives == string_list_cleaned

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            1,
            [1],
            1.1,
            [1.1],
            False,
            [False],
            True,
            [True],
            ["foo", 1],
        ],
    )
    def test_invalid_settings(value: str) -> None:
        """Test invalid settings."""
        with pytest.raises(TypeError, match="^Not a string or list of strings$"):
            config.RstcheckConfigFile(
                ignore_languages=value,
                ignore_directives=value,
                ignore_roles=value,
                ignore_substitutions=value,
                add_directives=value,
            )


class TestJoinRegexStrValidatorMethod:
    """Test ``join_regex_str`` validator method of the ``RstcheckConfig`` class.

    It validates the ``ignore_messages`` setting.
    """

    @staticmethod
    def test_none_means_unset() -> None:
        """Test ``None`` results in unset ignore_messages."""
        result = config.RstcheckConfigFile(ignore_messages=None)

        assert result is not None
        assert result.ignore_messages is None

    @staticmethod
    def test_passed_regex_is_kept() -> None:
        """Test passing a regex."""
        result = config.RstcheckConfigFile(ignore_messages=re.compile(""))

        assert result is not None
        assert isinstance(result.ignore_messages, re.Pattern)

    @staticmethod
    def test_strings_are_parsed_as_regex() -> None:
        """Test strings are parsed as regex."""
        string = r"\d{4}\.[A-Z]+Test$"
        regex = re.compile(string)

        result = config.RstcheckConfigFile(ignore_messages=string)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    def test_empty_strings_are_valid() -> None:
        """Test empty strings are parsed as regex too."""
        string = ""
        regex = re.compile(string)

        result = config.RstcheckConfigFile(ignore_messages=string)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    def test_string_list_are_joined_and_parsed_as_regex() -> None:
        """Test ignore_messages string lists are joined with "|" and parsed as regex."""
        string_list = [r"\d{4}\.[A-Z]+Test$", r"\d{4}\.[A-Z]+Test2$", r"\d{4}\.[A-Z]+Test3$"]
        full_string = r"\d{4}\.[A-Z]+Test$|\d{4}\.[A-Z]+Test2$|\d{4}\.[A-Z]+Test3$"
        regex = re.compile(full_string)

        result = config.RstcheckConfigFile(ignore_messages=string_list)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    @pytest.mark.parametrize(
        ("string_list", "full_string"), [([""], ""), (["", ""], "|"), ([], "")]
    )
    def test_list_with_empty_contents(string_list: list[str], full_string: str) -> None:
        """Test list with empty contents are parsed as regex too."""
        regex = re.compile(full_string)

        result = config.RstcheckConfigFile(ignore_messages=string_list)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            1,
            [1],
            1.1,
            [1.1],
            False,
            [False],
            True,
            [True],
            ["foo", 1],
        ],
    )
    def test_invalid_settings(value: str) -> None:
        """Test invalid ignore_messages settings."""
        with pytest.raises(TypeError, match="^Not a string or list of strings$"):
            config.RstcheckConfigFile(ignore_messages=value)


class TestIniFileLoader:
    """Test ``load_config_from_ini_file``."""

    @staticmethod
    def test_no_config_on_none() -> None:
        """Test no config is loaded if NONE is set."""
        conf_file = pathlib.Path("NONE")

        result = config._load_config_from_ini_file(conf_file)

        assert result is None

    @staticmethod
    def test_missing_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised on missing file."""
        conf_file = tmp_path / "config.ini"

        with pytest.raises(FileNotFoundError):
            config._load_config_from_ini_file(conf_file)

    @staticmethod
    def test_not_a_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised when not file."""
        conf_file = tmp_path

        with pytest.raises(FileNotFoundError):
            config._load_config_from_ini_file(conf_file)

    @staticmethod
    def test_returns_none_on_missing_section(tmp_path: pathlib.Path) -> None:
        """Test ``None`` is returned on missing section."""
        conf_file = tmp_path / "config.ini"
        file_content = "[not-rstcheck]"
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(conf_file)

        assert result is None

    @staticmethod
    def test_ignores_unsupported_settings(tmp_path: pathlib.Path) -> None:
        """Test unsupported settings are ignored."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        unsupported_feature=True
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(conf_file)

        assert result is not None

    @staticmethod
    def test_supported_settings_are_loaded(tmp_path: pathlib.Path) -> None:
        """Test supported settings are loaded."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        report_level=3
        ignore_directives=directive
        ignore_roles=role
        ignore_substitutions=substitution
        ignore_languages=language
        ignore_messages=message
        add_directives=add_directive
        """
        conf_file.write_text(file_content)
        regex = re.compile("message")

        result = config._load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR
        assert result.ignore_directives == ["directive"]
        assert result.ignore_roles == ["role"]
        assert result.ignore_substitutions == ["substitution"]
        assert result.ignore_languages == ["language"]
        assert result.ignore_messages == regex
        assert result.add_directives == ["add_directive"]

    @staticmethod
    def test_multiline_strings(tmp_path: pathlib.Path) -> None:
        """Test multiline strings are parsed."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        ignore_directives=directive
        ignore_roles=
            role1,
            role2,
            role3
        add_directives=add_directive
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.ignore_directives == ["directive"]
        assert result.ignore_roles == ["role1", "role2", "role3"]
        assert result.add_directives == ["add_directive"]

    @staticmethod
    def test_multiline_strings_trailing_comma(tmp_path: pathlib.Path) -> None:
        """Test multiline strings with trailing comma are parsed."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        ignore_directives=directive
        ignore_roles=
            role1,
            role2,
            role3,
        add_directives=add_directive
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.ignore_directives == ["directive"]
        assert result.ignore_roles == ["role1", "role2", "role3"]
        assert result.add_directives == ["add_directive"]

    @staticmethod
    def test_file_with_mixed_supported_settings(tmp_path: pathlib.Path) -> None:
        """Test mix of supported and unsupported settings."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        report_level=3
        ignore_directives=directive
        unsupported_feature=True
        add_directives=req,req-sw
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR
        assert result.ignore_directives == ["directive"]
        assert result.add_directives == ["req", "req-sw"]

    @staticmethod
    def test_file_with_mixed_supported_sections(tmp_path: pathlib.Path) -> None:
        """Test mix of rstcheck and other section."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        report_level=3
        ignore_directives=directive
        unsupported_feature=True
        add_directives=req,req-sw

        [not-rstcheck]
        report_level=2
        ignore_directives=not-directive
        unsupported_feature=False
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR
        assert result.ignore_directives == ["directive"]
        assert result.add_directives == ["req", "req-sw"]

    @staticmethod
    def test_warning_is_logged_on_missing_section_by_default(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test if a warning is logged on missing section."""
        conf_file = tmp_path / "config.ini"
        file_content = "[checkrst]"
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(conf_file)

        assert result is None
        assert f"Config file has no [rstcheck] section: '{conf_file}'." in caplog.text

    @staticmethod
    def test_warning_on_missing_section_can_be_info(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test if the warning logged on missing section can be an info."""
        conf_file = tmp_path / "config.ini"
        file_content = "[checkrst]"
        conf_file.write_text(file_content)
        caplog.set_level(logging.INFO)

        result = config._load_config_from_ini_file(conf_file, log_missing_section_as_warning=False)

        assert result is None
        assert f"Config file has no [rstcheck] section: '{conf_file}'." in caplog.text

    @staticmethod
    def test_dont_warning_on_unknown_settings_by_default(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that no warning is logged on unknown setting by default."""
        conf_file = tmp_path / "config.ini"
        file_content = """
[rstcheck]
report_level=INFO
unkwown_setting=true
"""
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(
            conf_file,
            log_missing_section_as_warning=False,
        )

        assert result is not None
        assert not caplog.text

    @staticmethod
    def test_warning_on_unknown_settings_when_set(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that a warning is logged on unknown setting when activated."""
        conf_file = tmp_path / "config.ini"
        file_content = """
[rstcheck]
report_level=INFO
unkwown_setting=true
"""
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(
            conf_file,
            log_missing_section_as_warning=False,
            warn_unknown_settings=True,
        )

        assert result is not None
        assert (
            f"Unknown setting(s) ['unkwown_setting'] found in file: '{conf_file}'." in caplog.text
        )

    @staticmethod
    def test_no_warning_on_known_settings_when_set(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that a warning is logged on known settings when activated."""
        conf_file = tmp_path / "config.ini"
        file_content = """
[rstcheck]
report_level=INFO
"""
        conf_file.write_text(file_content)

        result = config._load_config_from_ini_file(
            conf_file,
            log_missing_section_as_warning=False,
            warn_unknown_settings=True,
        )

        assert result is not None
        assert not caplog.text


@pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
class TestTomlFileLoader:
    """Test ``load_config_from_toml_file``."""

    @staticmethod
    def test_no_config_on_none() -> None:
        """Test no config is loaded if NONE is set."""
        conf_file = pathlib.Path("NONE")

        result = config._load_config_from_toml_file(conf_file)

        assert result is None

    @staticmethod
    def test_wrong_file_suffix_errors(tmp_path: pathlib.Path) -> None:
        """Test ``ValueError`` is raised on wrong file suffix."""
        conf_file = tmp_path / "config.ini"
        conf_file.touch()

        with pytest.raises(ValueError, match="^File is not a TOML file$"):
            config._load_config_from_toml_file(conf_file)

    @staticmethod
    def test_missing_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised on missing file."""
        conf_file = tmp_path / "config.toml"

        with pytest.raises(FileNotFoundError):
            config._load_config_from_toml_file(conf_file)

    @staticmethod
    def test_not_a_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised when not file."""
        conf_file = tmp_path / "config.toml"
        conf_file.mkdir()

        with pytest.raises(FileNotFoundError):
            config._load_config_from_toml_file(conf_file)

    @staticmethod
    @pytest.mark.parametrize("invalid_section", ["[tool.not-rstcheck]", "[rstcheck]"])
    def test_returns_none_on_missing_section(tmp_path: pathlib.Path, invalid_section: str) -> None:
        """Test ``None`` is returned on missing section."""
        conf_file = tmp_path / "config.toml"
        conf_file.write_text(invalid_section)

        result = config._load_config_from_toml_file(conf_file)

        assert result is None

    @staticmethod
    def test_ignores_unsupported_settings(tmp_path: pathlib.Path) -> None:
        """Test unsupported settings are ignored."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        unsupported_feature = true
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None

    @staticmethod
    def test_supported_settings_are_loaded(tmp_path: pathlib.Path) -> None:
        """Test supported settings are loaded."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        report_level = 3
        ignore_directives = ["directive"]
        ignore_roles = ["role"]
        ignore_substitutions = ["substitution"]
        ignore_languages = ["language"]
        ignore_messages = "message"
        """
        conf_file.write_text(file_content)
        regex = re.compile("message")

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR
        assert result.ignore_directives == ["directive"]
        assert result.ignore_roles == ["role"]
        assert result.ignore_substitutions == ["substitution"]
        assert result.ignore_languages == ["language"]
        assert result.ignore_messages == regex

    @staticmethod
    def test_file_with_mixed_supported_settings(tmp_path: pathlib.Path) -> None:
        """Test mix of supported and unsupported settings."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        report_level = 3
        ignore_directives = ["directive"]
        unsupported_feature = true
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR
        assert result.ignore_directives == ["directive"]

    @staticmethod
    def test_file_with_mixed_supported_sections(tmp_path: pathlib.Path) -> None:
        """Test mix of rstcheck and other section."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        report_level = 3
        ignore_directives = ["directive"]
        unsupported_feature = true

        [tool.not-rstcheck]
        report_level = 2
        ignore_directives = "not-directive"
        unsupported_feature = false
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR
        assert result.ignore_directives == ["directive"]

    @staticmethod
    @pytest.mark.parametrize(
        ("value", "parsed_value"),
        [
            ("none", config.ReportLevel.NONE),
            ("ERROR", config.ReportLevel.ERROR),
            ("1", config.ReportLevel.INFO),
            ("3", config.ReportLevel.ERROR),
        ],
    )
    def test_report_level_as_strings(
        tmp_path: pathlib.Path, value: str, parsed_value: config.ReportLevel
    ) -> None:
        """Test report setting with string values."""
        conf_file = tmp_path / "config.toml"
        file_content = f"""[tool.rstcheck]
        report_level = "{value}"
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report_level == parsed_value

    @staticmethod
    @pytest.mark.parametrize(
        ("value", "parsed_value"),
        [
            (1, config.ReportLevel.INFO),
            (3, config.ReportLevel.ERROR),
            (5, config.ReportLevel.NONE),
        ],
    )
    def test_report_level_as_int(
        tmp_path: pathlib.Path, value: int, parsed_value: config.ReportLevel
    ) -> None:
        """Test report setting with integer values."""
        conf_file = tmp_path / "config.toml"
        file_content = f"""[tool.rstcheck]
        report_level = {value}
        """
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report_level == parsed_value

    @staticmethod
    def test_ignore_messages_as_str(tmp_path: pathlib.Path) -> None:
        """Test ignore_messages setting with string value."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        ignore_messages = "some-regex"
        """
        conf_file.write_text(file_content)
        regex = re.compile("some-regex")

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    def test_ignore_messages_as_list(tmp_path: pathlib.Path) -> None:
        """Test ignore_messages setting with list of strings value."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        ignore_messages = ["some-regex", "another-regex"]
        """
        conf_file.write_text(file_content)
        regex = re.compile(r"some-regex|another-regex")

        result = config._load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    def test_warning_is_logged_on_missing_section_by_default(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test if a warning is logged on missing section."""
        conf_file = tmp_path / "config.toml"
        file_content = "[tool.checkrst]"
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(conf_file)

        assert result is None
        assert f"Config file has no [tool.rstcheck] section: '{conf_file}'." in caplog.text

    @staticmethod
    def test_warning_on_missing_section_can_be_info(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test if the warning logged on missing section can be an info."""
        conf_file = tmp_path / "config.toml"
        file_content = "[tool.checkrst]"
        conf_file.write_text(file_content)
        caplog.set_level(logging.INFO)

        result = config._load_config_from_toml_file(conf_file, log_missing_section_as_warning=False)

        assert result is None
        assert f"Config file has no [tool.rstcheck] section: '{conf_file}'." in caplog.text

    @staticmethod
    def test_dont_warning_on_unknown_settings_by_default(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that no warning is logged on unknown setting by default."""
        conf_file = tmp_path / "config.toml"
        file_content = """
[tool.rstcheck]
report_level="INFO"
unkwown_setting=true
"""
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(
            conf_file,
            log_missing_section_as_warning=False,
        )

        assert result is not None
        assert not caplog.text

    @staticmethod
    def test_warning_on_unknown_settings_when_set(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that a warning is logged on unknown setting when activated."""
        conf_file = tmp_path / "config.toml"
        file_content = """
[tool.rstcheck]
report_level="INFO"
unkwown_setting=true
"""
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(
            conf_file,
            log_missing_section_as_warning=False,
            warn_unknown_settings=True,
        )

        assert result is not None
        assert (
            f"Unknown setting(s) ['unkwown_setting'] found in file: '{conf_file}'." in caplog.text
        )

    @staticmethod
    def test_no_warning_on_known_settings_when_set(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that a warning is logged on known settings when activated."""
        conf_file = tmp_path / "config.toml"
        file_content = """
[tool.rstcheck]
report_level="INFO"
"""
        conf_file.write_text(file_content)

        result = config._load_config_from_toml_file(
            conf_file,
            log_missing_section_as_warning=False,
            warn_unknown_settings=True,
        )

        assert result is not None
        assert not caplog.text


class TestConfigFileLoader:
    """Test ``load_config_file``."""

    @staticmethod
    def test_no_config_on_none() -> None:
        """Test no config is loaded if NONE is set."""
        conf_file = pathlib.Path("NONE")

        result = config.load_config_file(conf_file)

        assert result is None

    @staticmethod
    @pytest.mark.parametrize("ini_file", [".rstcheck.cfg", "setup.cfg", "config.ini", "config.cfg"])
    def test_ini_files(tmp_path: pathlib.Path, ini_file: str) -> None:
        """Test with INI files."""
        conf_file = tmp_path / ini_file
        file_content = """[rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    @pytest.mark.parametrize("toml_file", [".rstcheck.toml", "setup.toml", "config.toml"])
    def test_toml_files(tmp_path: pathlib.Path, toml_file: str) -> None:
        """Test with TOML files."""
        conf_file = tmp_path / toml_file
        file_content = """[tool.rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR


class TestConfigDirLoader:
    """Test ``load_config_file_from_dir``."""

    @staticmethod
    def test_no_config_on_none() -> None:
        """Test no config is loaded if NONE is set."""
        conf_file = pathlib.Path("NONE")

        result = config.load_config_file_from_dir(conf_file)

        assert result is None

    @staticmethod
    @pytest.mark.parametrize("ini_file", [".rstcheck.cfg", "setup.cfg"])
    def test_supported_ini_files(tmp_path: pathlib.Path, ini_file: str) -> None:
        """Test with supported INI files."""
        conf_file = tmp_path / ini_file
        file_content = """[rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    @pytest.mark.parametrize("ini_file", ["config.ini", "config.cfg"])
    def test_unsupported_ini_files(tmp_path: pathlib.Path, ini_file: str) -> None:
        """Test with unsupported INI files."""
        conf_file = tmp_path / ini_file
        file_content = """[rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is None

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    @pytest.mark.parametrize("toml_file", ["pyproject.toml"])
    def test_supported_toml_files(tmp_path: pathlib.Path, toml_file: str) -> None:
        """Test with supported TOML files."""
        conf_file = tmp_path / toml_file
        file_content = """[tool.rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    @pytest.mark.parametrize("toml_file", [".rstcheck.toml", "setup.toml", "config.toml"])
    def test_unsupported_toml_files(tmp_path: pathlib.Path, toml_file: str) -> None:
        """Test with unsupported TOML files."""
        conf_file = tmp_path / toml_file
        file_content = """[tool.rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is None

    @staticmethod
    def test_rstcheck_over_setup(tmp_path: pathlib.Path) -> None:
        """Test .rstcheck.cfg takes precedence over setup.cfg."""
        setup_conf_file = tmp_path / "setup.cfg"
        setup_file_content = """[rstcheck]
        report_level = 2
        """
        setup_conf_file.write_text(setup_file_content)
        rstcheck_conf_file = tmp_path / ".rstcheck.cfg"
        rstcheck_file_content = """[rstcheck]
        report_level = 3
        """
        rstcheck_conf_file.write_text(rstcheck_file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    def test_rstcheck_over_pyproject(tmp_path: pathlib.Path) -> None:
        """Test .rstcheck.cfg takes precedence over pyproject.toml."""
        pyproject_conf_file = tmp_path / "pyproject.toml"
        pyproject_file_content = """[tool.rstcheck]
        report_level = 2
        """
        pyproject_conf_file.write_text(pyproject_file_content)
        rstcheck_conf_file = tmp_path / ".rstcheck.cfg"
        rstcheck_file_content = """[rstcheck]
        report_level = 3
        """
        rstcheck_conf_file.write_text(rstcheck_file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    def test_pyproject_over_setup(tmp_path: pathlib.Path) -> None:
        """Test pyproject.toml takes precedence over setup.cfg."""
        setup_conf_file = tmp_path / "setup.cfg"
        setup_file_content = """[rstcheck]
        report_level = 2
        """
        setup_conf_file.write_text(setup_file_content)
        pyproject_conf_file = tmp_path / "pyproject.toml"
        pyproject_file_content = """[tool.rstcheck]
        report_level = 3
        """
        pyproject_conf_file.write_text(pyproject_file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    def test_missing_config_means_next_file_is_checked(tmp_path: pathlib.Path) -> None:
        """Test missing config in file results in checking of next file."""
        setup_conf_file = tmp_path / "setup.cfg"
        setup_file_content = """[rstcheck]
        report_level = 3
        """
        setup_conf_file.write_text(setup_file_content)
        rstcheck_conf_file = tmp_path / ".rstcheck.cfg"
        rstcheck_file_content = """[not-rstcheck]
        report_level = 2
        """
        rstcheck_conf_file.write_text(rstcheck_file_content)

        result = config.load_config_file_from_dir(tmp_path)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_info_is_logged_on_no_config_found(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test if an info is logged if no config could be found."""
        conf_dir = tmp_path
        caplog.set_level(logging.INFO)

        result = config.load_config_file_from_dir(conf_dir)

        assert result is None
        assert (
            f"No config section in supported config files found in directory: '{conf_dir}'."
            in caplog.text
        )

    @staticmethod
    def test_warning_is_logged_on_no_config_section_in_rstcheck_file(
        tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test if an warning is logged if no config section could be found in .rstcheck.cfg."""
        conf_dir = tmp_path
        conf_file = conf_dir / ".rstcheck.cfg"
        file_content = "[checkrst]"
        conf_file.write_text(file_content)

        result = config.load_config_file_from_dir(conf_dir, log_missing_section_as_warning=False)

        assert result is None
        assert f"Config file has no [rstcheck] section: '{conf_file}'." in caplog.text


class TestConfigDirTreeLoader:
    """Test ``load_config_file_from_dir_tree``."""

    @staticmethod
    def test_no_config_on_none() -> None:
        """Test no config is loaded if NONE is set."""
        conf_file = pathlib.Path("NONE")

        result = config.load_config_file_from_dir_tree(conf_file)

        assert result is None

    @staticmethod
    def test_parent_searching(tmp_path: pathlib.Path) -> None:
        """Test option to search up the dir tree."""
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        unsupported_file = nested_dir / "config.cfg"
        unsupported_file_content = """[rstcheck]
        report_level = 2
        """
        unsupported_file.write_text(unsupported_file_content)
        supported_file = tmp_path / "setup.cfg"
        supported_file_content = """[rstcheck]
        report_level = 3
        """
        supported_file.write_text(supported_file_content)

        result = config.load_config_file_from_dir_tree(nested_dir)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_no_file_up_to_root(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
        """Test option to search up the dir tree with no file up to root dir."""
        root_dir = tmp_path
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        monkeypatch.setattr(pathlib.Path, "parent", root_dir)

        result = config.load_config_file_from_dir_tree(nested_dir)

        assert result is None

    @staticmethod
    def test_info_is_logged_on_no_config_found(
        tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test if an info is logged if no config could be found."""
        conf_dir = tmp_path
        caplog.set_level(logging.INFO)
        monkeypatch.setattr(pathlib.Path, "parent", conf_dir)

        result = config.load_config_file_from_dir_tree(conf_dir)

        assert result is None
        assert (
            f"No config section in supported config files found in directory tree: '{conf_dir}'."
            in caplog.text
        )


class TestConfigPathLoader:
    """Test ``load_config_file_from_path``."""

    @staticmethod
    def test_raises_on_nonexisting_path() -> None:
        """Test raises FileNotFoundError on path that is not a file or directory."""
        conf_file = pathlib.Path("does-not-exist-cfg")

        with pytest.raises(FileNotFoundError, match="Passed config path not found"):
            config.load_config_file_from_path(conf_file)

    @staticmethod
    def test_no_config_on_none() -> None:
        """Test no config is loaded if NONE is set."""
        conf_file = pathlib.Path("NONE")

        result = config.load_config_file_from_path(conf_file)

        assert result is None

    @staticmethod
    def test_with_file(tmp_path: pathlib.Path) -> None:
        """Test with INI file."""
        conf_file = tmp_path / ".rstcheck.cfg"
        file_content = """[rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file_from_path(conf_file)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_with_dir(tmp_path: pathlib.Path) -> None:
        """Test with directory."""
        conf_file = tmp_path / ".rstcheck.cfg"
        file_content = """[rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file_from_path(tmp_path)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_with_nested_dir(tmp_path: pathlib.Path) -> None:
        """Test with nested dir tree."""
        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()
        conf_file = tmp_path / "setup.cfg"
        file_content = """[rstcheck]
        report_level = 3
        """
        conf_file.write_text(file_content)

        result = config.load_config_file_from_path(nested_dir, search_dir_tree=True)

        assert result is not None
        assert result.report_level == config.ReportLevel.ERROR


class TestConfigMerger:
    """Test ``merge_configs``."""

    @staticmethod
    def test_default_merge_with_full_config() -> None:
        """Test config merging with full config."""
        config_base = config.RstcheckConfig(report_level=config.ReportLevel.SEVERE)
        config_add = config.RstcheckConfig(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add)

        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_default_merge_with_file_config() -> None:
        """Test config merging with file config."""
        config_base = config.RstcheckConfig(report_level=config.ReportLevel.SEVERE)
        config_add = config.RstcheckConfigFile(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add)

        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_default_merge_with_full_config_and_empty_base_config() -> None:
        """Test config merging with full config and empty base config."""
        config_base = config.RstcheckConfig()
        config_add = config.RstcheckConfig(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add)

        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_default_merge_with_file_config_and_empty_base_config() -> None:
        """Test config merging with file config and empty base config."""
        config_base = config.RstcheckConfig()
        config_add = config.RstcheckConfigFile(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add)

        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_default_merge_with_full_config_and_changed_dominance() -> None:
        """Test config merging with full config and changed dominance."""
        config_base = config.RstcheckConfig(report_level=config.ReportLevel.SEVERE)
        config_add = config.RstcheckConfig(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add, config_add_is_dominant=False)

        assert result.report_level == config.ReportLevel.SEVERE

    @staticmethod
    def test_default_merge_with_file_config_and_changed_dominance() -> None:
        """Test config merging with file config and changed dominance."""
        config_base = config.RstcheckConfig(report_level=config.ReportLevel.SEVERE)
        config_add = config.RstcheckConfigFile(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add, config_add_is_dominant=False)

        assert result.report_level == config.ReportLevel.SEVERE

    @staticmethod
    def test_default_merge_with_full_config_and_changed_dominance_and_empty_base_config() -> None:
        """Test config merging with full config, changed dominance and empty base config.

        Test ``None`` gets overwritten by set value.
        """
        config_base = config.RstcheckConfig()
        config_add = config.RstcheckConfig(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add, config_add_is_dominant=False)

        assert result.report_level == config.ReportLevel.ERROR

    @staticmethod
    def test_default_merge_with_file_config_and_changed_dominance_and_empty_base_config() -> None:
        """Test config merging with file config, changed dominance and empty base config.

        Test ``None`` gets overwritten by set value.
        """
        config_base = config.RstcheckConfig()
        config_add = config.RstcheckConfigFile(report_level=config.ReportLevel.ERROR)

        result = config.merge_configs(config_base, config_add, config_add_is_dominant=False)

        assert result.report_level == config.ReportLevel.ERROR
