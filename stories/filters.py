from django_filters import rest_framework as filters
from .models import Story

class StoryFilter(filters.FilterSet):
    author = filters.CharFilter(field_name="author__pen_name", lookup_expr="iexact")
    genre = filters.CharFilter(field_name="genre", lookup_expr="iexact")

    class Meta:
        model = Story
        fields = ["author", "genre"]
