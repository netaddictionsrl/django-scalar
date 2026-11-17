from django.test import SimpleTestCase, override_settings

from django_scalar import app_settings as module
from django_scalar.app_settings import app_settings
from django_scalar.checks import check_settings


class ScalarSettingsTests(SimpleTestCase):
    def test_defaults(self):
        self.assertEqual(app_settings.OPENAPI_URL, "/api/schema/")
        self.assertEqual(app_settings.TITLE, "Scalar API Reference")
        self.assertIsNone(app_settings.THEME)
        self.assertIsNone(app_settings.LAYOUT)
        self.assertIsNone(app_settings.DARK_MODE)
        self.assertIs(app_settings.HIDE_MODELS, False)
        self.assertIs(app_settings.HIDE_DOWNLOAD_BUTTON, False)
        self.assertIsNone(app_settings.SEARCH_HOTKEY)
        self.assertIsNone(app_settings.CUSTOM_CSS)
        self.assertEqual(app_settings.JS_URL, "https://cdn.jsdelivr.net/npm/@scalar/api-reference@latest")
        self.assertEqual(app_settings.PROXY_URL, "")
        self.assertEqual(app_settings.FAVICON_URL, "/static/favicon.ico")

    @override_settings(SCALAR_VERSION="1.32.10")
    def test_version_pins_the_default_js_url(self):
        self.assertEqual(app_settings.JS_URL, "https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.32.10")

    @override_settings(SCALAR_VERSION="1.32.10", SCALAR_JS_URL="https://example.com/scalar.js")
    def test_explicit_js_url_wins_over_version(self):
        self.assertEqual(app_settings.JS_URL, "https://example.com/scalar.js")

    @override_settings(SCALAR_TITLE="Custom")
    def test_module_attributes_read_the_current_settings(self):
        self.assertEqual(module.TITLE, "Custom")

    def test_unknown_setting_raises(self):
        with self.assertRaises(AttributeError):
            module.UNKNOWN_SETTING  # noqa: B018


class ChecksTests(SimpleTestCase):
    def test_default_settings_pass(self):
        self.assertEqual(check_settings(None), [])

    @override_settings(SCALAR_LAYOUT="classic", SCALAR_SEARCH_HOTKEY="k")
    def test_valid_settings_pass(self):
        self.assertEqual(check_settings(None), [])

    @override_settings(SCALAR_LAYOUT="", SCALAR_SEARCH_HOTKEY="")
    def test_empty_settings_count_as_unset(self):
        self.assertEqual(check_settings(None), [])

    @override_settings(SCALAR_LAYOUT="fancy")
    def test_unknown_layout_is_an_error(self):
        self.assertEqual([e.id for e in check_settings(None)], ["django_scalar.E001"])

    def test_hotkey_that_is_not_one_character_is_an_error(self):
        for value in ("ctrl+k", 7):
            with self.subTest(value=value), override_settings(SCALAR_SEARCH_HOTKEY=value):
                self.assertEqual([e.id for e in check_settings(None)], ["django_scalar.E002"])
