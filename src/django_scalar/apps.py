from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ScalarConfig(AppConfig):
    name = "django_scalar"
    verbose_name = _("Django Scalar")

    def ready(self):
        from . import checks  # noqa: F401 - registers the system checks
