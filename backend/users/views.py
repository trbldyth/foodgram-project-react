from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from djoser.views import UserViewSet
from .pagination import CustomPageNumberPagination
from .models import Subscribe
from .serializers import CustomUserSerializer, SubscribeSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = CustomPageNumberPagination


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscribe.objects.filter(user=user)
        context = {'request': request}
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscribeSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(subscriptions, many=True,
                                         context=context)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, user_id):
        user = request.user
        to_user = get_object_or_404(User, id=user_id)
        if user == to_user:
            return Response({'errors': 'You cannot subscribe yourself'},
                            status=HTTP_400_BAD_REQUEST)
        if Subscribe.objects.filter(user=user, author=to_user).exists():
            return Response({'errors': 'You already subscribed this user'},
                            status=HTTP_400_BAD_REQUEST)
        subscription = Subscribe.objects.create(user=user, author=to_user)
        serializer = SubscribeSerializer(subscription,
                                         context={'request': request})
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='subscribe')
    def unsubscribe(self, request, user_id):
        user = request.user
        to_user = get_object_or_404(User, id=user_id)
        subscription = Subscribe.objects.filter(user=user, author=to_user)
        if subscription.exists():
            subscription.delete()
        else:
            return Response({'error': 'Subscription does not exist'},
                            status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_204_NO_CONTENT)
