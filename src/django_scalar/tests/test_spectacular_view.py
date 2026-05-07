"""
Tests for the drf-spectacular-aware ScalarView.
"""

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse


@pytest.mark.django_db
class TestSpectacularScalarView:
    def test_resolves_schema_url_from_url_name(self, client):
        url = reverse("alt-scalar")
        response = client.get(url)
        assert response.status_code == 200

        soup = BeautifulSoup(response.content, "html.parser")
        api_reference = soup.find("script", id="api-reference")
        # The data-url should point at the schema URL we registered with name
        # "alt-schema" — i.e. /alt/api/schema/.
        assert api_reference["data-url"].endswith("/alt/api/schema/")

    def test_uses_configured_title(self, client):
        url = reverse("alt-scalar")
        response = client.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        assert soup.title.string == "Alt Docs"
