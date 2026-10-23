from django.urls import path
from .views import (
    SocialBroadcastView,
    SocialBroadcastDetailView,
    SocialPlatformConfigView,
    SocialPlatformConfigDetailView,
    SocialPostLogListView,
)

app_name = "django_social_autoposter"

urlpatterns = [
    # Broadcast Endpoints (Compose and Post at once)
    path('broadcast', SocialBroadcastView.as_view(), name='broadcast-list-create'),
    path('broadcast/', SocialBroadcastView.as_view(), name='broadcast-list-create-slash'),
    path('broadcast/<int:pk>', SocialBroadcastDetailView.as_view(), name='broadcast-detail'),
    path('broadcast/<int:pk>/', SocialBroadcastDetailView.as_view(), name='broadcast-detail-slash'),

    # Platform Configurations Endpoints
    path('configs', SocialPlatformConfigView.as_view(), name='config-list-create'),
    path('configs/', SocialPlatformConfigView.as_view(), name='config-list-create-slash'),
    path('configs/<int:pk>', SocialPlatformConfigDetailView.as_view(), name='config-detail'),
    path('configs/<int:pk>/', SocialPlatformConfigDetailView.as_view(), name='config-detail-slash'),

    # Audit Logs
    path('logs', SocialPostLogListView.as_view(), name='log-list'),
    path('logs/', SocialPostLogListView.as_view(), name='log-list-slash'),
]
