from django.test import SimpleTestCase
from django.urls import reverse


class SpectacularScalarViewTests(SimpleTestCase):
    def test_resolves_schema_url_from_url_name(self):
        response = self.client.get(reverse("alt-scalar"))
        self.assertEqual(response.context_data["openapi_url"], "/alt/api/schema/")
        self.assertContains(response, 'data-url="/alt/api/schema/"')

    def test_forwards_lang_and_version_to_the_schema_url(self):
        response = self.client.get(reverse("alt-scalar"), {"lang": "it", "version": "2"})
        self.assertEqual(response.context_data["openapi_url"], "/alt/api/schema/?lang=it&version=2")

    def test_uses_configured_title(self):
        response = self.client.get(reverse("alt-scalar"))
        self.assertContains(response, "<title>Alt Docs</title>", html=True)
