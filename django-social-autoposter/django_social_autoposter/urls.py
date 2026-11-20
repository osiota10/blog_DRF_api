from django.urls import path
from .views import (
    SocialBroadcastView,
    SocialBroadcastDetailView,
    SocialPlatformConfigView,
    SocialPlatformConfigDetailView,
    SocialPostLogListView,
    SocialMessageSendAPIView,
    SocialMessageListView,
    SocialMessageDetailView,
    SocialBroadcastCancelAPIView,
    SocialBroadcastPublishNowAPIView,
    SocialBroadcastRescheduleAPIView,
    SocialMessageCancelAPIView,
    SocialMessageSendNowAPIView,
    SocialMessageRescheduleAPIView,
    SocialScheduledOverviewAPIView,
)

app_name = "django_social_autoposter"

urlpatterns = [
    # Broadcast Endpoints (Compose and Post at once)
    path('broadcast', SocialBroadcastView.as_view(), name='broadcast-list-create'),
    path('broadcast/', SocialBroadcastView.as_view(), name='broadcast-list-create-slash'),
    path('broadcast/<int:pk>', SocialBroadcastDetailView.as_view(), name='broadcast-detail'),
    path('broadcast/<int:pk>/', SocialBroadcastDetailView.as_view(), name='broadcast-detail-slash'),
    path('broadcast/<int:pk>/cancel', SocialBroadcastCancelAPIView.as_view(), name='broadcast-cancel'),
    path('broadcast/<int:pk>/cancel/', SocialBroadcastCancelAPIView.as_view(), name='broadcast-cancel-slash'),
    path('broadcast/<int:pk>/publish-now', SocialBroadcastPublishNowAPIView.as_view(), name='broadcast-publish-now'),
    path('broadcast/<int:pk>/publish-now/', SocialBroadcastPublishNowAPIView.as_view(), name='broadcast-publish-now-slash'),
    path('broadcast/<int:pk>/reschedule', SocialBroadcastRescheduleAPIView.as_view(), name='broadcast-reschedule'),
    path('broadcast/<int:pk>/reschedule/', SocialBroadcastRescheduleAPIView.as_view(), name='broadcast-reschedule-slash'),

    # Platform Configurations Endpoints
    path('configs', SocialPlatformConfigView.as_view(), name='config-list-create'),
    path('configs/', SocialPlatformConfigView.as_view(), name='config-list-create-slash'),
    path('configs/<int:pk>', SocialPlatformConfigDetailView.as_view(), name='config-detail'),
    path('configs/<int:pk>/', SocialPlatformConfigDetailView.as_view(), name='config-detail-slash'),

    # Audit Logs
    path('logs', SocialPostLogListView.as_view(), name='log-list'),
    path('logs/', SocialPostLogListView.as_view(), name='log-list-slash'),

    # Direct Messaging Endpoints
    path('messages/send', SocialMessageSendAPIView.as_view(), name='message-send'),
    path('messages/send/', SocialMessageSendAPIView.as_view(), name='message-send-slash'),
    path('messages', SocialMessageListView.as_view(), name='message-list'),
    path('messages/', SocialMessageListView.as_view(), name='message-list-slash'),
    path('messages/<int:pk>', SocialMessageDetailView.as_view(), name='message-detail'),
    path('messages/<int:pk>/', SocialMessageDetailView.as_view(), name='message-detail-slash'),
    path('messages/<int:pk>/cancel', SocialMessageCancelAPIView.as_view(), name='message-cancel'),
    path('messages/<int:pk>/cancel/', SocialMessageCancelAPIView.as_view(), name='message-cancel-slash'),
    path('messages/<int:pk>/send-now', SocialMessageSendNowAPIView.as_view(), name='message-send-now'),
    path('messages/<int:pk>/send-now/', SocialMessageSendNowAPIView.as_view(), name='message-send-now-slash'),
    path('messages/<int:pk>/reschedule', SocialMessageRescheduleAPIView.as_view(), name='message-reschedule'),
    path('messages/<int:pk>/reschedule/', SocialMessageRescheduleAPIView.as_view(), name='message-reschedule-slash'),

    # Unified Scheduled Overview
    path('scheduled', SocialScheduledOverviewAPIView.as_view(), name='scheduled-overview'),
    path('scheduled/', SocialScheduledOverviewAPIView.as_view(), name='scheduled-overview-slash'),
]
