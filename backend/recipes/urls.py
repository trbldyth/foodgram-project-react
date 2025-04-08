from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet)

app_name = 'recipes'

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    re_path(r'^recipes/(?P<recipe_id>\d+)/favorite/$',
            FavoriteViewSet.as_view({
                'post': 'add_to_favorite',
                'delete': 'delete_from_favorite'
            })),
    re_path(r'^recipes/(?P<recipe_id>\d+)/shopping_cart/$',
            ShoppingCartViewSet.as_view({
                'post': 'add_to_shopping_cart',
                'delete': 'delete_from_shopping_cart'
            })),
    path('recipes/download_shopping_cart/',
         RecipeViewSet.as_view({'get': 'download_shopping_cart'})),
    path('', include(router.urls)),
]
