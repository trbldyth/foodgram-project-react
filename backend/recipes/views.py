from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN)

from users.pagination import CustomPageNumberPagination
from .filters import RecipeFilter, IngredientSearchFilter
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .pagination import CustomDataPagination
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from .permissions import CustomIsAuthenticated


def create_func(request, recipe_id, model, arg):
    try:
        user, recipe = request.user, Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        raise exceptions.ValidationError({'error': 'Recipe does not exist'})
    if model.objects.filter(user=user, recipe=recipe).exists():
        raise exceptions.ValidationError(
            {'errors': 'You already add this recipe to smth'})
    add_to_smth = model.objects.create(user=user,
                                       recipe=recipe)
    serializer = arg(add_to_smth,
                     context={'request': request})
    return Response(serializer.data, status=HTTP_201_CREATED)


def remove_func(request, recipe_id, model):
    user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)
    is_in_smth = model.objects.filter(user=user,
                                      recipe=recipe)
    if is_in_smth.exists():
        is_in_smth.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    else:
        raise exceptions.ValidationError({'error': 'Recipe is not in smth'})


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (CustomIsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(status=HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(status=HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=[item.recipe for item in shopping_cart_items]
        )
        ingredients_info = ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        content = ""
        for info in ingredients_info:
            content += (f"{info['ingredient__name']}: {info['amount']} "
                        f"{info['ingredient__measurement_unit']}\n")

        response = HttpResponse(
            content, content_type='application/octet-stream'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart_info.txt"'
        )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = CustomDataPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = CustomDataPagination
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (CustomIsAuthenticated,)
    pagination_class = CustomDataPagination

    @action(detail=True, methods=['post'], url_path='favorite',)
    def add_to_favorite(self, request, recipe_id):
        return create_func(request, recipe_id, Favorite, FavoriteSerializer)

    @action(detail=True, methods=['delete'], url_path='favorite')
    def delete_from_favorite(self, request, recipe_id):
        return remove_func(request, recipe_id, Favorite)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (CustomIsAuthenticated,)
    pagination_class = CustomDataPagination

    @action(detail=True, methods=['post'], url_path='shopping_cart',)
    def add_to_shopping_cart(self, request, recipe_id):
        return create_func(request, recipe_id, ShoppingCart,
                           ShoppingCartSerializer)

    @action(detail=True, methods=['delete'], url_path='shopping_cart',)
    def delete_from_shopping_cart(self, request, recipe_id):
        return remove_func(request, recipe_id, ShoppingCart)
