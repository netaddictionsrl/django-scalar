from django.test import SimpleTestCase
from django.urls import resolve, reverse

from django_scalar.views import scalar_viewer


class UrlsTests(SimpleTestCase):
    def test_docs_url(self):
        url = reverse("django_scalar:docs")
        self.assertEqual(url, "/scalar/api/docs/")
        self.assertEqual(resolve(url).func, scalar_viewer)

    def test_schema_url_is_registered_when_spectacular_is_installed(self):
        self.assertEqual(reverse("django_scalar:schema"), "/scalar/api/schema/")
