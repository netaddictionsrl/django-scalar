"""
Centralized settings access for django-scalar.

All settings are read from ``django.conf.settings`` and are prefixed with
``SCALAR_``. Sensible defaults are returned by the descriptors below when a
setting is not configured.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings


class ScalarSettings:
    """
    Centralized settings access for django-scalar.

    Reads settings prefixed with 'SCALAR_' from django.conf.settings.
    Default values are defined directly within the properties below.
    """

    PREFIX = "SCALAR_"

    @property
    def OPENAPI_URL(self) -> str:
        """URL to the OpenAPI schema. Defaults to ``/api/schema/``."""
        return getattr(settings, self.PREFIX + "OPENAPI_URL", "/api/schema/")

    @property
    def TITLE(self) -> str:
        """Page title. Defaults to ``Scalar API Reference``."""
        return getattr(settings, self.PREFIX + "TITLE", "Scalar API Reference")

    @property
    def THEME(self) -> str | None:
        """
        Theme for the Scalar viewer (``light``, ``dark``, ``moonlight``,
        ``purplehaze``, ``eclipse``, ``solarized``...). Defaults to ``None``
        (Scalar's default).
        """
        return getattr(settings, self.PREFIX + "THEME", None)

    @property
    def LAYOUT(self) -> str | None:
        """
        Scalar layout (``modern`` or ``classic``). Defaults to ``None`` so
        Scalar uses its own default.
        """
        return getattr(settings, self.PREFIX + "LAYOUT", None)

    @property
    def DARK_MODE(self) -> bool | None:
        """
        Force dark/light mode. ``True`` forces dark mode, ``False`` forces
        light mode, ``None`` (default) lets Scalar follow the OS preference.
        """
        return getattr(settings, self.PREFIX + "DARK_MODE", None)

    @property
    def HIDE_MODELS(self) -> bool:
        """If ``True`` hide the schema models section. Defaults to ``False``."""
        return getattr(settings, self.PREFIX + "HIDE_MODELS", False)

    @property
    def HIDE_DOWNLOAD_BUTTON(self) -> bool:
        """If ``True`` hide the download-OpenAPI button. Defaults to ``False``."""
        return getattr(settings, self.PREFIX + "HIDE_DOWNLOAD_BUTTON", False)

    @property
    def SEARCH_HOTKEY(self) -> str | None:
        """Single character used as the global search hotkey (e.g. ``k``)."""
        return getattr(settings, self.PREFIX + "SEARCH_HOTKEY", None)

    @property
    def CUSTOM_CSS(self) -> str | None:
        """Optional CSS injected as a ``<style>`` block in the page head."""
        return getattr(settings, self.PREFIX + "CUSTOM_CSS", None)

    @property
    def VERSION(self) -> str:
        """
        Version of ``@scalar/api-reference`` to load from the default jsdelivr
        CDN. Used only when ``JS_URL`` is left at its default. Pin a major
        like ``"1"`` or a specific version like ``"1.32.10"`` for production.
        Defaults to ``"latest"``.
        """
        return getattr(settings, self.PREFIX + "VERSION", "latest")

    @property
    def JS_URL(self) -> str:
        """
        URL to the Scalar JS library. Defaults to a jsdelivr URL pinned to
        ``SCALAR_VERSION``.
        """
        default = f"https://cdn.jsdelivr.net/npm/@scalar/api-reference@{self.VERSION}"
        return getattr(settings, self.PREFIX + "JS_URL", default)

    @property
    def PROXY_URL(self) -> str:
        """URL for the Scalar CORS proxy service. Defaults to ``''``."""
        return getattr(settings, self.PREFIX + "PROXY_URL", "")

    @property
    def FAVICON_URL(self) -> str:
        """Favicon URL. Defaults to ``/static/favicon.ico``."""
        return getattr(settings, self.PREFIX + "FAVICON_URL", "/static/favicon.ico")


# Create a single, accessible instance of the settings class
app_settings = ScalarSettings()

# Implement PEP 562 for module-level attribute access.
# This allows importing settings like `from django_scalar.app_settings import TITLE`.
_KNOWN_SETTINGS_ATTRS = {
    "OPENAPI_URL",
    "TITLE",
    "THEME",
    "LAYOUT",
    "DARK_MODE",
    "HIDE_MODELS",
    "HIDE_DOWNLOAD_BUTTON",
    "SEARCH_HOTKEY",
    "CUSTOM_CSS",
    "VERSION",
    "JS_URL",
    "PROXY_URL",
    "FAVICON_URL",
}


def __getattr__(name: str) -> Any:
    if name == "app_settings":
        return app_settings
    if name in _KNOWN_SETTINGS_ATTRS:
        return getattr(app_settings, name)
    raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")
