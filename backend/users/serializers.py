from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import Subscribe
from recipes.models import Recipe
from recipes.serializers import RecipeShortInfoSerializer

User = get_user_model()


def get_is_subscribed(obj, serializer_field):
    request = serializer_field.context.get('request')
    if request is None or not request.user.is_authenticated:
        return False
    return Subscribe.objects.filter(user=request.user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'password',
                  'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return get_is_subscribed(obj, self)

    def to_representation(self, instance):
        if instance.is_anonymous:
            raise AuthenticationFailed("Anonymous user")
        return super().to_representation(instance)


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count',)

    def get_is_subscribed(self, obj):
        return get_is_subscribed(obj.author, self)

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit is not None:
            recipes = recipes[:int(limit)]
        return RecipeShortInfoSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return recipes.count()
