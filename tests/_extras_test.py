"""Tests for ``_extras`` module."""
import pytest

from rstcheck_core import _compat, _extras


class TestInstallChecker:
    """Test ``is_installed_with_supported_version``."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_false_on_missing_sphinx_package() -> None:
        """Test install-checker returns ``False`` when ``sphinx`` is missing."""
        result = _extras.is_installed_with_supported_version("sphinx")

        assert result is False

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_true_on_installed_sphinx_package() -> None:
        """Test install-checker returns ``True`` when ``sphinx`` is installed with good version."""
        result = _extras.is_installed_with_supported_version("sphinx")

        assert result is True

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_false_on_installed_sphinx_package_too_old(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test install-checker returns ``False`` when ``sphinx`` is installed with bad version."""
        monkeypatch.setattr(_compat, "version", lambda _: "0.0")

        result = _extras.is_installed_with_supported_version("sphinx")

        assert result is False


class TestInstallGuard:
    """Test ``install_guard``."""

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_error_on_missing_sphinx_package() -> None:
        """Test install-guard raises exception when ``sphinx`` is missing."""
        with pytest.raises(ModuleNotFoundError):
            _extras.install_guard("sphinx")  # act

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_ok_on_installed_sphinx_package() -> None:
        """Test install-guard doesn't raise when ``sphinx`` is installed."""
        _extras.install_guard("sphinx")  # act


class TestTomliInstallGuard:
    """Test ``install_guard_tomli``."""

    @staticmethod
    @pytest.mark.skipif(_extras.TOMLI_INSTALLED, reason="Test without tomli extra.")
    def test_error_tomllib_imported_is_false_and_on_missing_tomli_package() -> None:
        """Test install-guard raises exception when ``tomllib_imported`` is :py:obj:`False` and ``tomli`` is missing."""  # noqa: B950
        with pytest.raises(ModuleNotFoundError):
            _extras.install_guard_tomli(False)  # act

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on tomli extra.")
    def test_ok_when_tomllib_imported_is_false_and_tomli_package_is_installed() -> None:
        """Test install-guard doesn't raise when ``tomllib_imported`` is :py:obj:`False` but ``tomli`` is installed."""  # noqa: B950
        _extras.install_guard_tomli(False)  # act

    @staticmethod
    def test_ok_when_tomllib_imported_is_true() -> None:
        """Test install-guard doesn't raise when ``tomllib_imported`` is :py:obj:`True`."""
        _extras.install_guard_tomli(True)  # act
