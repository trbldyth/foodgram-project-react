from django.contrib.auth import get_user_model
from django.db import models
from colorfield.fields import ColorField
User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=128,
                            verbose_name='Ingredient title')
    measurement_unit = models.CharField(
        max_length=16, verbose_name='Measurement unit')

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=128, unique=True, verbose_name='Tag title')
    color = ColorField(
        default='#FF0000', unique=True, verbose_name='Tag color')
    slug = models.SlugField(
        blank=False, unique=True, verbose_name='Tag slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Recipe author')
    name = models.CharField(
        max_length=128, blank=False, verbose_name='Recipe title')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        blank=False,
        verbose_name='Recipe image'
    )
    text = models.TextField(
        blank=False, verbose_name='Description')
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes', verbose_name='Ingredient list')
    tags = models.ManyToManyField(
        Tag, through='TagRecipe', verbose_name='Tag list')
    cooking_time = models.PositiveSmallIntegerField(
        blank=False, verbose_name='Cooking Time')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Publication Date')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.tag} {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='user_favorite', verbose_name='User')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_favorite', verbose_name="User's favorite recipe")

    class Meta:
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorites'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='user_sc', verbose_name='User')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_sc',
        verbose_name="Recipe that user added to cart")

    class Meta:
        verbose_name = 'Shopping cart'
        verbose_name_plural = 'Shopping cart'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipes_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='used_in_recipes')
    amount = models.PositiveSmallIntegerField(default=0)
