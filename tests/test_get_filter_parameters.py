import uuid

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


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        app_label = "tests"


class Editor(Author):
    class Meta:
        app_label = "tests"


class ChiefEditor(Editor):
    class Meta:
        app_label = "tests"


class AuthorFilterSet(FilterSet):
    name = CharFilter(lookup_expr="iexact")
    age = NumberFilter()
    is_active = BooleanFilter()
    created_at = DateFilter()
    status = ChoiceFilter(choices=[("active", "Active"), ("inactive", "Inactive")])
    friend = ModelChoiceFilter(queryset=Author.objects.all())
    friend_name = ModelChoiceFilter(queryset=Author.objects.all(), to_field_name="name")
    friend_pk = ModelChoiceFilter(queryset=Author.objects.all(), to_field_name="pk")
    chief = ModelChoiceFilter(queryset=ChiefEditor.objects.all())
    book = ModelChoiceFilter(queryset=Book.objects.all())

    class Meta:
        model = Author
        fields = ("name", "age", "is_active", "created_at")


class GetFilterParametersTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parameters = {p.name: p for p in get_filter_parameters(AuthorFilterSet)}

    def test_one_optional_query_parameter_per_filter(self):
        self.assertEqual(len(self.parameters), 10)
        for parameter in self.parameters.values():
            self.assertEqual(parameter.location, "query")
            self.assertIs(parameter.required, False)

    def test_types(self):
        types = {name: p.type for name, p in self.parameters.items()}
        self.assertEqual(
            types,
            {
                "name": str,
                "age": int,
                "is_active": bool,
                "created_at": str,
                "status": str,
                # a related object is named by its primary key, or by to_field_name
                "friend": int,
                "friend_name": str,
                "friend_pk": int,
                # the key of an inherited model is the key of its root
                "chief": int,
                "book": str,
            },
        )

    def test_choices_become_an_enum(self):
        self.assertEqual(self.parameters["status"].enum, ["active", "inactive"])

    def test_descriptions(self):
        self.assertEqual(self.parameters["name"].description, "Filter by exact name (case-insensitive)")
        self.assertEqual(self.parameters["age"].description, "Filter by age")
        self.assertEqual(self.parameters["friend"].description, "ID of related Author")
