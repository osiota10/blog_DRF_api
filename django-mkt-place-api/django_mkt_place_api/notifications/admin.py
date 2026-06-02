from django.contrib import admin
from .models import Notification, NotificationPreference, PushToken, NotificationLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('is_read', 'priority', 'notification_type')
    search_fields = ('user__email', 'title', 'message')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'push_order_updates', 'email_promotions', 'sms_delivery_alerts')
    search_fields = ('user__email',)

@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'is_active', 'created_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('user__email', 'token', 'device_name')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'channel', 'status', 'sent_at', 'delivered_at')
    list_filter = ('channel', 'status')
    search_fields = ('user__email', 'error_message')
