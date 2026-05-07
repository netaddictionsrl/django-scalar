"""
Views for rendering the Scalar API Reference inside Django.

The function-based ``scalar_viewer`` is the original entry point and stays
backwards compatible. ``SpectacularScalarView`` is a thin class-based wrapper
intended for projects that already use ``drf-spectacular``: drop it into your
URLConf the same way you would drop ``SpectacularSwaggerView``.
"""

from __future__ import annotations

import json
from typing import Any

from django.template.response import TemplateResponse
from django.views.generic import View

from . import app_settings as _settings


def _build_context(
    *,
    openapi_url: str | None = None,
    title: str | None = None,
    scalar_theme: str | None = None,
    scalar_layout: str | None = None,
    dark_mode: bool | None = None,
    hide_models: bool | None = None,
    hide_download_button: bool | None = None,
    search_hotkey: str | None = None,
    custom_css: str | None = None,
    scalar_js_url: str | None = None,
    scalar_proxy_url: str | None = None,
    scalar_favicon_url: str | None = None,
) -> dict[str, Any]:
    """Build the template context, falling back to ``SCALAR_*`` settings."""

    def _coalesce(override: Any, default: Any) -> Any:
        return override if override is not None else default

    final_theme = _coalesce(scalar_theme, _settings.THEME)
    final_layout = _coalesce(scalar_layout, _settings.LAYOUT)
    final_dark_mode = _coalesce(dark_mode, _settings.DARK_MODE)
    final_hide_models = _coalesce(hide_models, _settings.HIDE_MODELS)
    final_hide_download = _coalesce(hide_download_button, _settings.HIDE_DOWNLOAD_BUTTON)
    final_search_hotkey = _coalesce(search_hotkey, _settings.SEARCH_HOTKEY)

    # Build the Scalar JS configuration object. Keys are omitted when they
    # are None/False so we don't override Scalar's own defaults.
    configuration: dict[str, Any] = {}
    if final_theme:
        configuration["theme"] = final_theme
    if final_layout:
        configuration["layout"] = final_layout
    if final_dark_mode is not None:
        configuration["darkMode"] = bool(final_dark_mode)
    if final_hide_models:
        configuration["hideModels"] = True
    if final_hide_download:
        configuration["hideDownloadButton"] = True
    if final_search_hotkey:
        configuration["searchHotKey"] = final_search_hotkey

    return {
        "openapi_url": _coalesce(openapi_url, _settings.OPENAPI_URL),
        "title": _coalesce(title, _settings.TITLE),
        # Kept individually for backwards-compatible template/test access.
        "theme": final_theme,
        "layout": final_layout,
        "dark_mode": final_dark_mode,
        "hide_models": final_hide_models,
        "hide_download_button": final_hide_download,
        "search_hotkey": final_search_hotkey,
        "custom_css": _coalesce(custom_css, _settings.CUSTOM_CSS),
        "scalar_js_url": _coalesce(scalar_js_url, _settings.JS_URL),
        "scalar_proxy_url": _coalesce(scalar_proxy_url, _settings.PROXY_URL),
        "scalar_favicon_url": _coalesce(scalar_favicon_url, _settings.FAVICON_URL),
        # Pre-serialized JSON ready to be dropped into the template.
        "configuration_json": json.dumps(configuration) if configuration else "",
    }


def scalar_viewer(
    request,
    openapi_url: str | None = None,
    title: str | None = None,
    scalar_theme: str | None = None,
    scalar_layout: str | None = None,
    dark_mode: bool | None = None,
    hide_models: bool | None = None,
    hide_download_button: bool | None = None,
    search_hotkey: str | None = None,
    custom_css: str | None = None,
    scalar_js_url: str | None = None,
    scalar_proxy_url: str | None = None,
    scalar_favicon_url: str | None = None,
) -> TemplateResponse:
    """
    Render the Scalar API Reference viewer.

    Defaults are sourced from ``django_scalar.app_settings``. Any keyword
    argument set to a non-``None`` value overrides the corresponding setting,
    which makes it easy to mount multiple Scalar instances with different
    configuration in the same project.
    """
    context = _build_context(
        openapi_url=openapi_url,
        title=title,
        scalar_theme=scalar_theme,
        scalar_layout=scalar_layout,
        dark_mode=dark_mode,
        hide_models=hide_models,
        hide_download_button=hide_download_button,
        search_hotkey=search_hotkey,
        custom_css=custom_css,
        scalar_js_url=scalar_js_url,
        scalar_proxy_url=scalar_proxy_url,
        scalar_favicon_url=scalar_favicon_url,
    )
    return TemplateResponse(request, "django_scalar/scalar.html", context)


class ScalarView(View):
    """
    Class-based equivalent of :func:`scalar_viewer`.

    Configure with class attributes or by passing kwargs to ``as_view()``::

        path(
            "api/docs/",
            ScalarView.as_view(title="My API", scalar_theme="moonlight"),
            name="scalar-docs",
        )
    """

    openapi_url: str | None = None
    title: str | None = None
    scalar_theme: str | None = None
    scalar_layout: str | None = None
    dark_mode: bool | None = None
    hide_models: bool | None = None
    hide_download_button: bool | None = None
    search_hotkey: str | None = None
    custom_css: str | None = None
    scalar_js_url: str | None = None
    scalar_proxy_url: str | None = None
    scalar_favicon_url: str | None = None

    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs):  # noqa: D401 - Django view signature
        return scalar_viewer(
            request,
            openapi_url=self.openapi_url,
            title=self.title,
            scalar_theme=self.scalar_theme,
            scalar_layout=self.scalar_layout,
            dark_mode=self.dark_mode,
            hide_models=self.hide_models,
            hide_download_button=self.hide_download_button,
            search_hotkey=self.search_hotkey,
            custom_css=self.custom_css,
            scalar_js_url=self.scalar_js_url,
            scalar_proxy_url=self.scalar_proxy_url,
            scalar_favicon_url=self.scalar_favicon_url,
        )


def _import_spectacular_view():
    """Lazily import :class:`SpectacularAPIView` so drf-spectacular stays optional."""
    try:
        from drf_spectacular.views import SpectacularAPIView
    except ImportError as exc:  # pragma: no cover - import-guard branch
        raise ImportError(
            "SpectacularScalarView requires drf-spectacular. Install the "
            "'spectacular' extra: pip install 'django-scalar[spectacular]'."
        ) from exc
    return SpectacularAPIView


class SpectacularScalarView(ScalarView):
    """
    Drop-in replacement for ``SpectacularSwaggerView`` / ``SpectacularRedocView``.

    When wired to a named schema URL via ``url_name`` (or a literal ``url``),
    the view resolves the schema URL at render time and passes it to Scalar
    as ``openapi_url``. This mirrors how drf-spectacular's own UI views work::

        from django_scalar.views import SpectacularScalarView

        urlpatterns = [
            path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
            path(
                "api/docs/",
                SpectacularScalarView.as_view(url_name="schema"),
                name="scalar-docs",
            ),
        ]
    """

    url_name: str | None = None
    url: str | None = None

    def __init_subclass__(cls, **kwargs: Any) -> None:  # pragma: no cover
        super().__init_subclass__(**kwargs)
        # Touch the import early so misconfigured environments fail fast at
        # subclass definition time rather than during a request.
        _import_spectacular_view()

    def get(self, request, *args, **kwargs):  # noqa: D401 - Django view signature
        # Resolve the schema URL the same way drf-spectacular does.
        if self.url_name is not None or self.url is not None:
            # Imported lazily so drf-spectacular stays an optional dependency.
            from drf_spectacular.plumbing import (
                get_relative_url,
                set_query_parameters,
            )
            from rest_framework.reverse import reverse

            schema_url = self.url or get_relative_url(reverse(self.url_name, request=request))
            schema_url = set_query_parameters(
                url=schema_url,
                lang=request.GET.get("lang"),
                version=request.GET.get("version"),
            )
        else:
            schema_url = self.openapi_url

        return scalar_viewer(
            request,
            openapi_url=schema_url,
            title=self.title,
            scalar_theme=self.scalar_theme,
            scalar_layout=self.scalar_layout,
            dark_mode=self.dark_mode,
            hide_models=self.hide_models,
            hide_download_button=self.hide_download_button,
            search_hotkey=self.search_hotkey,
            custom_css=self.custom_css,
            scalar_js_url=self.scalar_js_url,
            scalar_proxy_url=self.scalar_proxy_url,
            scalar_favicon_url=self.scalar_favicon_url,
        )
