# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-05-07

Forked and maintained by [Netaddiction](https://github.com/netaddictionsrl).

### Added

- New class-based view `ScalarView` plus `SpectacularScalarView`, a drop-in
  replacement for `SpectacularSwaggerView`/`SpectacularRedocView` that
  resolves the schema URL via `url_name` or `url`.
- New `SCALAR_VERSION` setting that pins the bundled `@scalar/api-reference`
  version on the default jsdelivr CDN. Useful for production (no surprise
  bumps from `@latest`).
- New configuration knobs surfaced from Scalar:
  `SCALAR_LAYOUT`, `SCALAR_DARK_MODE`, `SCALAR_HIDE_MODELS`,
  `SCALAR_HIDE_DOWNLOAD_BUTTON`, `SCALAR_SEARCH_HOTKEY`, `SCALAR_CUSTOM_CSS`.
  All are also exposed as keyword arguments on `scalar_viewer` and as class
  attributes on `ScalarView`.
- Test matrix now exercises Django 4.2 / 5.0 / 5.1 / 5.2 across Python
  3.10 – 3.13.

### Changed

- **`drf-spectacular` and `django-filter` are now optional dependencies.**
  The package itself only depends on Django. Install one of the new extras
  for the optional integrations:
  - `pip install "django-scalar[spectacular]"` for `SpectacularScalarView`
    and the auto-registered `api/schema/` URL.
  - `pip install "django-scalar[filters]"` for the `get_filter_parameters`
    helper.
  - `pip install "django-scalar[all]"` to get everything.
- Default `SCALAR_JS_URL` is now derived from `SCALAR_VERSION`
  (`https://cdn.jsdelivr.net/npm/@scalar/api-reference@latest` by default).
  An explicit `SCALAR_JS_URL` still wins.
- `urls.py` no longer hard-imports `drf_spectacular`. The schema URL is only
  registered when the optional extra is installed.
- The Scalar configuration object is now built server-side and serialized
  into the page as a single JSON blob, instead of constructed inline in the
  template.
- Project metadata updated: homepage, source and issues now point at the
  Netaddiction fork.

### Fixed

- `get_filter_parameters` previously overwrote the `ModelChoiceFilter`
  description with a generic one because the description-by-lookup branch
  ran unconditionally. The ModelChoiceFilter description is now preserved.

## [0.2.0] - 2025-05-02

- v0.2.0 feat: introduce configurable Scalar view and app settings (#3)
- Add `app_settings` for centralized SCALAR_* default management
- Add tests for custom configuration and theme behavior
- Add installation and usage details to README.md

### Changed

- Updated `scalar_viewer` with custom parameters and theme support
- Updated `scalar.html` for conditional theme handling

### Removed

- Unnecessary Swagger UI (rendered via DRF-Spectacular) from urls.py

## [0.1.8] - 2025-04-29

### Added

- Added test suite for views, `get_filter_parameters`, and URLs
- Added end-to-end tests that verify HTML contains the expected context data
- Added end-to-end tests that verify the overall structure and integrity of the HTML document
- Add [pre-commit](https://pre-commit.org) configuration for consistent development

### Changed

 - Changed project maintainer dependencies to use dependency-groups (installed with `--group` flag)
  instead of optional-dependencies (installed with `--extra` flag).
 - Change `scalar_viewer` to return a `TemplateResponse` instead of `HttpResponse`
 - Update QA (linting) to using pre-commit, including: ruff, mypy, djlint, etc.

## [0.1.7] - 2025-04-25

### Added

- v0.1.7 (#7) Split HTML/CSS into templates and static files.
- v0.1.7 Default to the most recent Python versions: 3.10, 3.11, 3.12, and 3.13

### Fixed

- v0.1.7 Fix bad indentation in the return statement in `get_filter_parameters.py` (#5).
- v0.1.7 Fix import error in urls.py (importing scalar_viewer from .scalar instead of .views).

## [0.1.6] - 2025-04-24

## Added
 - v0.1.6 (#4) Add ruff linting to CI pipelines
