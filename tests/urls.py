from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from django_scalar.views import SpectacularScalarView

urlpatterns = [
    path("scalar/", include("django_scalar.urls")),
    path("alt/api/schema/", SpectacularAPIView.as_view(), name="alt-schema"),
    path("alt/api/docs/", SpectacularScalarView.as_view(url_name="alt-schema", title="Alt Docs"), name="alt-scalar"),
]
