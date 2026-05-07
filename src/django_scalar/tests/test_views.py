"""
Tests for the views module.
"""

import json

import pytest
from bs4 import BeautifulSoup
from django.test import RequestFactory, override_settings
from django.urls import reverse

from django_scalar.views import ScalarView, scalar_viewer


@pytest.mark.django_db
class TestScalarViewer:
    """Tests for the scalar_viewer view function."""

    def test_scalar_viewer_returns_200(self, client):
        url = reverse("django_scalar:docs")
        response = client.get(url)
        assert response.status_code == 200

    def test_scalar_viewer_uses_correct_template(self, client):
        url = reverse("django_scalar:docs")
        response = client.get(url)
        assert "django_scalar/scalar.html" in [t.name for t in response.templates]

    def test_scalar_viewer_context(self):
        request = RequestFactory().get("/")
        response = scalar_viewer(request)

        ctx = response.context_data
        for key in (
            "openapi_url",
            "title",
            "theme",
            "scalar_js_url",
            "scalar_proxy_url",
            "scalar_favicon_url",
            "configuration_json",
        ):
            assert key in ctx

        assert ctx["openapi_url"] == "/api/schema/"
        assert ctx["title"] == "Scalar API Reference"
        assert ctx["theme"] is None
        assert ctx["scalar_js_url"] == ("https://cdn.jsdelivr.net/npm/@scalar/api-reference@latest")
        assert ctx["scalar_proxy_url"] == ""
        assert ctx["scalar_favicon_url"] == "/static/favicon.ico"
        # No theme/layout/etc. configured -> empty configuration block
        assert ctx["configuration_json"] == ""

    def test_scalar_viewer_with_custom_parameters(self):
        request = RequestFactory().get("/")
        response = scalar_viewer(
            request,
            openapi_url="/custom/schema/",
            title="Custom API Reference",
            scalar_theme="purple",
            scalar_layout="classic",
            dark_mode=True,
            hide_models=True,
            hide_download_button=True,
            search_hotkey="k",
            custom_css="body { background: red; }",
            scalar_js_url="https://example.com/scalar.js",
            scalar_proxy_url="https://example.com/proxy/",
            scalar_favicon_url="/custom/favicon.ico",
        )

        ctx = response.context_data
        assert ctx["openapi_url"] == "/custom/schema/"
        assert ctx["title"] == "Custom API Reference"
        assert ctx["theme"] == "purple"
        assert ctx["layout"] == "classic"
        assert ctx["dark_mode"] is True
        assert ctx["hide_models"] is True
        assert ctx["hide_download_button"] is True
        assert ctx["search_hotkey"] == "k"
        assert ctx["custom_css"] == "body { background: red; }"
        assert ctx["scalar_js_url"] == "https://example.com/scalar.js"
        assert ctx["scalar_proxy_url"] == "https://example.com/proxy/"
        assert ctx["scalar_favicon_url"] == "/custom/favicon.ico"

        config = json.loads(ctx["configuration_json"])
        assert config == {
            "theme": "purple",
            "layout": "classic",
            "darkMode": True,
            "hideModels": True,
            "hideDownloadButton": True,
            "searchHotKey": "k",
        }

    def test_html_content_contains_context_data(self, client):
        url = reverse("django_scalar:docs")
        response = client.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        assert soup.title.string == "Scalar API Reference"

        favicon_link = soup.find("link", rel="shortcut icon")
        assert favicon_link["href"] == "/static/favicon.ico"

        api_reference_script = soup.find("script", id="api-reference")
        assert api_reference_script["data-url"] == "/api/schema/"
        assert api_reference_script["data-proxy-url"] == ""

        scalar_js_script = soup.find_all("script")[-1]
        assert scalar_js_script["src"].startswith("https://cdn.jsdelivr.net/npm/@scalar/api-reference")

    def test_html_structure_integrity(self, client):
        url = reverse("django_scalar:docs")
        response = client.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        assert soup.html["lang"] == "en"
        assert soup.head is not None
        assert soup.body is not None

        meta_charset = soup.find("meta", charset="utf-8")
        assert meta_charset is not None

        meta_viewport = soup.find("meta", attrs={"name": "viewport"})
        assert meta_viewport is not None
        assert "width=device-width" in meta_viewport["content"]

        noscript = soup.find("noscript")
        assert noscript is not None
        assert "Scalar requires Javascript" in noscript.text

        css_link = soup.find("link", rel="stylesheet")
        assert css_link is not None

    def test_theme_configuration_in_html(self):
        request = RequestFactory().get("/")
        response = scalar_viewer(request, scalar_theme="purple")
        response.render()

        soup = BeautifulSoup(response.content.decode(), "html.parser")

        api_reference_script = soup.find("script", id="api-reference")
        config_script = api_reference_script.find_next("script")

        assert config_script is not None
        assert "configuration" in config_script.text
        assert "theme" in config_script.text
        assert "purple" in config_script.text

    @override_settings(SCALAR_VERSION="1.32.10")
    def test_version_setting_pins_default_js_url(self):
        request = RequestFactory().get("/")
        response = scalar_viewer(request)
        assert response.context_data["scalar_js_url"] == "https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.32.10"

    @override_settings(
        SCALAR_VERSION="1.32.10",
        SCALAR_JS_URL="https://example.com/custom.js",
    )
    def test_explicit_js_url_wins_over_version(self):
        request = RequestFactory().get("/")
        response = scalar_viewer(request)
        assert response.context_data["scalar_js_url"] == "https://example.com/custom.js"

    def test_custom_css_rendered_in_head(self):
        request = RequestFactory().get("/")
        response = scalar_viewer(request, custom_css=".x { color: red; }")
        response.render()

        soup = BeautifulSoup(response.content.decode(), "html.parser")
        styles = [s.get_text() for s in soup.head.find_all("style")]
        assert any(".x { color: red; }" in s for s in styles)


@pytest.mark.django_db
class TestScalarView:
    """Tests for the class-based ScalarView."""

    def test_get_returns_template_response(self):
        request = RequestFactory().get("/")
        view = ScalarView.as_view(title="CBV Title")
        response = view(request)
        assert response.status_code == 200
        assert response.context_data["title"] == "CBV Title"

    def test_disallows_post(self):
        request = RequestFactory().post("/")
        view = ScalarView.as_view()
        response = view(request)
        assert response.status_code == 405
