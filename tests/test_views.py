import json

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse

from django_scalar.views import ScalarView, scalar_viewer


class ScalarViewerTests(SimpleTestCase):
    def test_default_page(self):
        response = self.client.get(reverse("django_scalar:docs"))
        self.assertTemplateUsed(response, "django_scalar/scalar.html")
        self.assertContains(response, "<title>Scalar API Reference</title>", html=True)
        self.assertContains(response, '<link rel="shortcut icon" href="/static/favicon.ico" />', html=True)
        self.assertContains(response, '<link rel="stylesheet" href="/static/css/scalar.css" />', html=True)
        self.assertContains(response, 'data-url="/api/schema/"')
        self.assertContains(response, 'data-proxy-url=""')
        self.assertContains(
            response, '<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@latest"></script>'
        )
        # Nothing configured: Scalar keeps its own defaults
        self.assertEqual(response.context_data["configuration_json"], "")
        self.assertNotContains(response, "dataset.configuration")

    def test_custom_parameters(self):
        response = scalar_viewer(
            RequestFactory().get("/"),
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
        context = response.context_data
        self.assertEqual(context["openapi_url"], "/custom/schema/")
        self.assertEqual(context["title"], "Custom API Reference")
        self.assertEqual(context["custom_css"], "body { background: red; }")
        self.assertEqual(context["scalar_js_url"], "https://example.com/scalar.js")
        self.assertEqual(context["scalar_proxy_url"], "https://example.com/proxy/")
        self.assertEqual(context["scalar_favicon_url"], "/custom/favicon.ico")
        self.assertEqual(
            json.loads(context["configuration_json"]),
            {
                "theme": "purple",
                "layout": "classic",
                "darkMode": True,
                "hideModels": True,
                "hideDownloadButton": True,
                "searchHotKey": "k",
            },
        )
        html = response.render().content.decode()
        self.assertIn("dataset.configuration", html)
        self.assertIn("purple", html)
        self.assertInHTML("<style>body { background: red; }</style>", html)

    def test_dark_mode_false_forces_light_mode(self):
        response = scalar_viewer(RequestFactory().get("/"), dark_mode=False)
        self.assertEqual(json.loads(response.context_data["configuration_json"]), {"darkMode": False})

    @override_settings(SCALAR_THEME="moonlight", SCALAR_TITLE="From settings")
    def test_settings_are_the_defaults_and_arguments_override_them(self):
        response = scalar_viewer(RequestFactory().get("/"), title="From argument")
        self.assertEqual(response.context_data["title"], "From argument")
        self.assertEqual(response.context_data["theme"], "moonlight")


class ScalarViewTests(SimpleTestCase):
    def test_get_uses_the_view_attributes(self):
        response = ScalarView.as_view(title="CBV Title")(RequestFactory().get("/"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["title"], "CBV Title")

    def test_post_is_not_allowed(self):
        response = ScalarView.as_view()(RequestFactory().post("/"))
        self.assertEqual(response.status_code, 405)
