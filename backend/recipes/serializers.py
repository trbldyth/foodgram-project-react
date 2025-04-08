from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import (Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)

User = get_user_model()


def get_is_authenticated(request):
    return request is not None and request.user.is_authenticated


def get_is_favorited(obj, serializer_field):
    request = serializer_field.context.get('request')
    if get_is_authenticated(request):
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()
    return False


def get_is_in_shopping_cart(obj, serializer_field):
    request = serializer_field.context.get('request')
    if get_is_authenticated(request):
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()
    return False


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient',)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipes_ingredients')
    image = Base64ImageField(required=True, allow_null=False)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart')
    cooking_time = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time',)
        read_only_field = ('pub_date')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipes_ingredients')
        new_recipe = Recipe.objects.create(**validated_data)
        new_recipe.tags.set(tags)
        self.get_ingredients(new_recipe, ingredients_data)
        return new_recipe

    def update(self, instance, validated_data):
        if 'tags' not in validated_data:
            raise serializers.ValidationError('Tags field is required')
        if 'recipes_ingredients' not in validated_data:
            raise serializers.ValidationError('Ingredient field is required')
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipes_ingredients')
        validated_data.pop('author', None)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(tags_data)
        self.get_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        from users.serializers import CustomUserSerializer
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        representation['author'] = CustomUserSerializer(instance.author).data
        return representation

    def validate_image(self, value):
        if value is None:
            raise serializers.ValidationError("The image field is required.")
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("Tags field cannot be empty.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Tags field cannot contain duplicate values.")
        return value

    def validate_ingredients(self, ingredients_data):
        if not ingredients_data:
            raise serializers.ValidationError(
                "Ingredients field cannot be empty.")
        ingredient_list = []
        for ingredient_data in ingredients_data:
            if (not ingredient_data.get('ingredient')
                    or not ingredient_data.get('amount')):
                raise serializers.ValidationError(
                    "Ingredient should have an ingredient and amount field")
            ingredient = ingredient_data.get('ingredient')
            ingredient_list.append(ingredient)
        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError()
        return ingredients_data

    def get_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    def get_is_favorited(self, obj):
        return get_is_favorited(obj, self)

    def get_is_in_shopping_cart(self, obj):
        return get_is_in_shopping_cart(obj, self)


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'cooking_time', 'image')

    def get_is_favorited(self, obj):
        return get_is_favorited(obj.recipe, self)


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'cooking_time', 'image')

    def get_is_in_shopping_cart(self, obj):
        return get_is_in_shopping_cart(obj.recipe, self)
