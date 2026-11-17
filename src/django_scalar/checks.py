from django.core.checks import Error, register

from .app_settings import app_settings

LAYOUTS = ("modern", "classic")


@register()
def check_settings(app_configs, **kwargs):
    """The settings Scalar would silently ignore when wrong hold a value it accepts."""
    errors = []
    layout = app_settings.LAYOUT
    if layout is not None and layout not in LAYOUTS:
        errors.append(
            Error(
                f"SCALAR_LAYOUT = {layout!r} is not a Scalar layout.",
                hint=f"Set it to one of {', '.join(map(repr, LAYOUTS))}, or leave it unset.",
                id="django_scalar.E001",
            )
        )
    hotkey = app_settings.SEARCH_HOTKEY
    if hotkey is not None and not (isinstance(hotkey, str) and len(hotkey) == 1):
        errors.append(
            Error(
                f"SCALAR_SEARCH_HOTKEY = {hotkey!r} is not a single character.",
                hint='Set it to one letter, e.g. "k", or leave it unset.',
                id="django_scalar.E002",
            )
        )
    return errors
