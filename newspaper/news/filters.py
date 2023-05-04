import django_filters
from django_filters import FilterSet, ModelChoiceFilter, DateTimeFilter
from django.forms import DateTimeInput
from .models import Post, Category


class PostFilter(FilterSet):
    posted_after = django_filters.DateTimeFilter(
        field_name='post_datetime',
        lookup_expr='gt',
        label='Created after:',
        widget=DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        )
    )

    class Meta:
        model = Post
        fields = {'post_name': ['icontains'], 'post_category': ['exact']}
