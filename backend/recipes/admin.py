from django.contrib import admin

from .models import Recipe, Tag, Ingredient, Favorite, ShoppingCart

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
