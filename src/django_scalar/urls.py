"""
Default URL configuration for django-scalar.

drf-spectacular is an *optional* dependency. If it is installed, this module
exposes a ready-to-use schema endpoint at ``api/schema/`` so that the
``scalar_viewer`` view can find an OpenAPI document at the default
``SCALAR_OPENAPI_URL``. If drf-spectacular is not installed, only the Scalar
viewer URL is registered, and you are expected to provide the OpenAPI schema
yourself (configure ``SCALAR_OPENAPI_URL`` accordingly).
"""

from django.urls import path

from .views import scalar_viewer

app_name = "django_scalar"

urlpatterns: list = [
    path("api/docs/", scalar_viewer, name="docs"),
]

try:
    from drf_spectacular.views import SpectacularAPIView
except ImportError:  # pragma: no cover - exercised only when extra is missing
    SpectacularAPIView = None  # type: ignore[assignment]

if SpectacularAPIView is not None:
    urlpatterns = [
        # Endpoint below needs to match {openapi_url} from views.scalar_viewer
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        *urlpatterns,
    ]
