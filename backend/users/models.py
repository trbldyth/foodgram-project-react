from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='EMail'
    )
    first_name = models.CharField(
        max_length=32, verbose_name='First Name')
    last_name = models.CharField(
        max_length=32, verbose_name='Last Name')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriber', verbose_name='Subscriber')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribing', verbose_name='Author')

    class Meta:
        unique_together = ('user', 'author',)
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
