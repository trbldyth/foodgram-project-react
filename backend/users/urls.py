from django.urls import include, path, re_path

from .views import SubscribeViewSet

app_name = 'users'

urlpatterns = [
    path('users/subscriptions/',
         SubscribeViewSet.as_view({'get': 'subscriptions'})),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    re_path(r'^users/(?P<user_id>\d+)/subscribe/$',
            SubscribeViewSet.as_view({
                'post': 'subscribe',
                'delete': 'unsubscribe'
            })),
]
