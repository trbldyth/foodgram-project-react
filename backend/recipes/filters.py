from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_by_favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_by_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_by_favorite(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipe_favorite__user=user)
        return queryset

    def filter_by_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipe_sc__user=user)
        return queryset


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
