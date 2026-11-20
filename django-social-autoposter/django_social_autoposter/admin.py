from django.contrib import admin
from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog, SocialDirectMessage


class SocialPostLogInline(admin.TabularInline):
    model = SocialPostLog
    extra = 0
    readonly_fields = ('platform', 'status', 'external_post_id', 'external_post_url', 'error_message', 'created_at')
    can_delete = False


@admin.register(SocialPlatformConfig)
class SocialPlatformConfigAdmin(admin.ModelAdmin):
    list_display = ('platform', 'is_enabled', 'page_or_account_id', 'updated_at')
    list_filter = ('is_enabled', 'platform')
    search_fields = ('platform', 'page_or_account_id')


@admin.register(SocialBroadcast)
class SocialBroadcastAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'scheduled_at', 'published_at', 'message_snippet', 'target_platforms', 'created_at')
    list_filter = ('status', 'created_at', 'scheduled_at')
    search_fields = ('title', 'message')
    inlines = [SocialPostLogInline]

    def message_snippet(self, obj):
        return obj.message[:50] + ("..." if len(obj.message) > 50 else "")
    message_snippet.short_description = "Message"


@admin.register(SocialPostLog)
class SocialPostLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'broadcast', 'platform', 'status', 'external_post_id', 'created_at')
    list_filter = ('status', 'platform', 'created_at')
    search_fields = ('platform', 'external_post_id', 'error_message')


@admin.register(SocialDirectMessage)
class SocialDirectMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'platform', 'recipient_id', 'direction', 'status', 'scheduled_at', 'sent_at', 'external_message_id', 'created_at')
    list_filter = ('platform', 'status', 'direction', 'scheduled_at', 'created_at')
    search_fields = ('recipient_id', 'sender_id', 'external_message_id', 'message')

