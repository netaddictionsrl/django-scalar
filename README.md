# Django Scalar API Reference

A Django app that renders the beautiful [Scalar API Reference](https://github.com/scalar/scalar)
viewer for any OpenAPI schema your project serves.

This is a maintained fork by [Netaddiction](https://github.com/netaddictionsrl)
of the original [oerd/django-scalar](https://github.com/oerd/django-scalar).

## Highlights

- Function-based **and** class-based views (`scalar_viewer`, `ScalarView`).
- First-class drf-spectacular integration via `SpectacularScalarView` — drop-in
  replacement for `SpectacularSwaggerView` / `SpectacularRedocView`.
- `drf-spectacular` and `django-filter` are **optional** extras: a base install
  only depends on Django.
- Pinnable Scalar bundle via `SCALAR_VERSION` (default points at
  `@scalar/api-reference@latest` on jsdelivr).
- Configurable theme, layout, dark mode, search hotkey, custom CSS, and more.
- Multiple, differently configured Scalar instances per project.

## Installation

Install only the Scalar viewer (Django-only):

```bash
pip install "django-scalar @ git+https://github.com/netaddictionsrl/django-scalar@v0.3.0"
# or with uv
uv add "django-scalar @ git+https://github.com/netaddictionsrl/django-scalar@v0.3.0"
```

If you want the drf-spectacular integration:

```bash
pip install "django-scalar[spectacular] @ git+https://github.com/netaddictionsrl/django-scalar@v0.3.0"
```

Add `django_scalar` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_scalar",
]
```

## Quick start (drf-spectacular)

```python
# urls.py
from django.urls import path
from drf_spectacular.views import SpectacularAPIView

from django_scalar.views import SpectacularScalarView

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularScalarView.as_view(url_name="schema"),
        name="api-docs",
    ),
]
```

`SpectacularScalarView` resolves the schema URL via `reverse()` exactly the
way `SpectacularSwaggerView` does, so it slots into existing
drf-spectacular setups with one line.

## Quick start (any OpenAPI document)

If you serve your schema yourself (no drf-spectacular needed), use the
function-based view:

```python
from django.urls import path
from django_scalar.views import scalar_viewer

urlpatterns = [
    path("api/docs/", scalar_viewer, name="scalar-docs"),
]
```

Then point `SCALAR_OPENAPI_URL` at your schema:

```python
SCALAR_OPENAPI_URL = "/static/openapi.yaml"
```

## Settings

All settings live in `django.conf.settings` and use the `SCALAR_` prefix.
None are required — sensible defaults are provided.

| Setting | Default | Notes |
|---|---|---|
| `SCALAR_OPENAPI_URL` | `"/api/schema/"` | URL Scalar fetches the schema from. |
| `SCALAR_TITLE` | `"Scalar API Reference"` | `<title>` and tab name. |
| `SCALAR_THEME` | `None` | `light`, `dark`, `moonlight`, `purplehaze`, `eclipse`, `solarized`, `bluePlanet`, `saturn`, `kepler`, `mars`, `deepSpace`, `none`. |
| `SCALAR_LAYOUT` | `None` | `modern` or `classic`. |
| `SCALAR_DARK_MODE` | `None` | `True`/`False` to force, `None` follows OS preference. |
| `SCALAR_HIDE_MODELS` | `False` | Hide the schema models section. |
| `SCALAR_HIDE_DOWNLOAD_BUTTON` | `False` | Hide the OpenAPI download button. |
| `SCALAR_SEARCH_HOTKEY` | `None` | One letter (e.g. `"k"`). |
| `SCALAR_CUSTOM_CSS` | `None` | Raw CSS injected into `<head>`. |
| `SCALAR_VERSION` | `"latest"` | `@scalar/api-reference` version pinned in the default `SCALAR_JS_URL`. Pin to a real version (e.g. `"1.32.10"`) in production. |
| `SCALAR_JS_URL` | jsdelivr URL pinned to `SCALAR_VERSION` | Override to self-host. |
| `SCALAR_PROXY_URL` | `""` | Optional Scalar CORS proxy. |
| `SCALAR_FAVICON_URL` | `"/static/favicon.ico"` |  |

## Multiple instances

Pass keyword arguments to `scalar_viewer` (FBV) or set class attributes on
`ScalarView`/`SpectacularScalarView` (CBV) to mount multiple, differently
configured Scalar pages in one project:

```python
urlpatterns = [
    path(
        "api/v1/docs/",
        SpectacularScalarView.as_view(url_name="schema-v1", title="API v1"),
        name="docs-v1",
    ),
    path(
        "api/v2/docs/",
        SpectacularScalarView.as_view(
            url_name="schema-v2",
            title="API v2",
            scalar_theme="moonlight",
        ),
        name="docs-v2",
    ),
]
```

## `get_filter_parameters`

Helper that turns a `django_filters.FilterSet` into a list of
`drf_spectacular.utils.OpenApiParameter`. Requires the `filters` extra:

```bash
pip install "django-scalar[filters]"
```

```python
from drf_spectacular.utils import extend_schema
from django_scalar.get_filter_parameters import get_filter_parameters

@extend_schema(parameters=get_filter_parameters(MyFilterSet))
class MyView(ListAPIView):
    ...
```

## Development

```bash
uv sync --group test --group qa
uv run pytest
uv run ruff check src
```

## Contributing

Issues and pull requests welcome on
[github.com/netaddictionsrl/django-scalar](https://github.com/netaddictionsrl/django-scalar).
