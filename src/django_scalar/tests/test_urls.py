"""
Tests for the URLs configuration.
"""

from django.urls import resolve, reverse

from django_scalar.views import scalar_viewer


class TestUrls:
    def test_scalar_viewer_url_resolves(self):
        url = reverse("django_scalar:docs")
        assert resolve(url).func == scalar_viewer

    def test_scalar_viewer_url_name(self):
        from tests.urls import PREFIX

        url = reverse("django_scalar:docs")
        assert url == f"/{PREFIX}/api/docs/"

    def test_schema_url_registered_when_spectacular_installed(self):
        # drf-spectacular is in the test dependency group, so the schema URL
        # should be registered alongside the docs URL.
        url = reverse("django_scalar:schema")
        assert url.endswith("/api/schema/")
