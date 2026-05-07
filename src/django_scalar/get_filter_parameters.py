"""
Helper that turns a ``django_filters.FilterSet`` into a list of
``drf_spectacular.utils.OpenApiParameter`` so that filter query params
appear in the generated OpenAPI schema.

Both ``django-filter`` and ``drf-spectacular`` are optional dependencies of
``django-scalar``. Install the ``filters`` extra to use this helper::

    pip install "django-scalar[filters]"
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing-only imports
    from drf_spectacular.utils import OpenApiParameter


def get_filter_parameters(filter_class: type[Any]) -> list[Any]:
    """
    Automatically generate OpenAPI parameters from a FilterSet class.

    Args:
        filter_class: The FilterSet class to generate parameters from.

    Returns:
        List of ``OpenApiParameter`` objects (possibly empty).

    Raises:
        ImportError: If ``django-filter`` or ``drf-spectacular`` is not
            installed. Install the ``filters`` extra to use this helper.
    """
    try:
        from django_filters.filters import (
            BooleanFilter,
            ChoiceFilter,
            DateFilter,
            ModelChoiceFilter,
            NumberFilter,
        )
        from drf_spectacular.utils import OpenApiParameter
        from rest_framework.fields import DecimalField
    except ImportError as exc:  # pragma: no cover - import-guard branch
        raise ImportError(
            "get_filter_parameters requires django-filter, drf-spectacular and "
            "djangorestframework. Install the 'filters' extra: "
            "pip install 'django-scalar[filters]'."
        ) from exc

    parameters: list[OpenApiParameter] = []

    for field_name, filter_instance in filter_class().filters.items():
        parameter_type: type = str  # default type
        enum: list | None = None

        # Determine parameter type based on filter type
        if isinstance(filter_instance, NumberFilter):
            parameter_type = float if isinstance(filter_instance.field, DecimalField) else int
        elif isinstance(filter_instance, BooleanFilter):
            parameter_type = bool
        elif isinstance(filter_instance, DateFilter):
            parameter_type = str
        elif isinstance(filter_instance, ChoiceFilter):
            parameter_type = str
            enum = [choice[0] for choice in filter_instance.extra["choices"]]
        elif isinstance(filter_instance, ModelChoiceFilter):
            parameter_type = int

        # Get lookup expression for description
        lookup_expr = getattr(filter_instance, "lookup_expr", "exact")

        if isinstance(filter_instance, ModelChoiceFilter):
            description = f"ID of related {filter_instance.field.queryset.model.__name__}"
        elif lookup_expr == "icontains":
            description = f"Filter by {field_name} (case-insensitive, partial match)"
        elif lookup_expr == "gte":
            description = f"Filter by {field_name} (greater than or equal)"
        elif lookup_expr == "lte":
            description = f"Filter by {field_name} (less than or equal)"
        elif lookup_expr == "iexact":
            description = f"Filter by exact {field_name} (case-insensitive)"
        else:
            description = f"Filter by {field_name}"

        parameters.append(
            OpenApiParameter(
                name=field_name,
                type=parameter_type,
                location="query",
                description=description,
                required=False,
                enum=enum,
            )
        )

    return parameters
