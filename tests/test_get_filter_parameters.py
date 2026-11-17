from django.db import models
from django.test import SimpleTestCase
from django_filters import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    DateFilter,
    FilterSet,
    ModelChoiceFilter,
    NumberFilter,
)

from django_scalar.get_filter_parameters import get_filter_parameters


class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        app_label = "tests"


class AuthorFilterSet(FilterSet):
    name = CharFilter(lookup_expr="iexact")
    age = NumberFilter()
    is_active = BooleanFilter()
    created_at = DateFilter()
    status = ChoiceFilter(choices=[("active", "Active"), ("inactive", "Inactive")])
    friend = ModelChoiceFilter(queryset=Author.objects.all())

    class Meta:
        model = Author
        fields = ("name", "age", "is_active", "created_at")


class GetFilterParametersTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parameters = {p.name: p for p in get_filter_parameters(AuthorFilterSet)}

    def test_one_optional_query_parameter_per_filter(self):
        self.assertEqual(list(self.parameters), ["name", "age", "is_active", "created_at", "status", "friend"])
        for parameter in self.parameters.values():
            self.assertEqual(parameter.location, "query")
            self.assertIs(parameter.required, False)

    def test_types(self):
        types = {name: p.type for name, p in self.parameters.items()}
        self.assertEqual(
            types, {"name": str, "age": int, "is_active": bool, "created_at": str, "status": str, "friend": int}
        )

    def test_choices_become_an_enum(self):
        self.assertEqual(self.parameters["status"].enum, ["active", "inactive"])

    def test_descriptions(self):
        self.assertEqual(self.parameters["name"].description, "Filter by exact name (case-insensitive)")
        self.assertEqual(self.parameters["age"].description, "Filter by age")
        self.assertEqual(self.parameters["friend"].description, "ID of related Author")
