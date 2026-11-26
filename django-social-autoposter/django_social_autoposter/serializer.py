from rest_framework import serializers
from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog, SocialDirectMessage


class SocialPlatformConfigSerializer(serializers.ModelSerializer):
    has_access_token = serializers.SerializerMethodField()
    has_access_token_secret = serializers.SerializerMethodField()
    has_api_key = serializers.SerializerMethodField()
    has_api_secret = serializers.SerializerMethodField()
    has_bearer_token = serializers.SerializerMethodField()

    def get_has_access_token(self, obj):
        return bool(obj.access_token)

    def get_has_access_token_secret(self, obj):
        return bool(obj.access_token_secret)

    def get_has_api_key(self, obj):
        return bool(obj.api_key)

    def get_has_api_secret(self, obj):
        return bool(obj.api_secret)

    def get_has_bearer_token(self, obj):
        return bool(obj.bearer_token)

    class Meta:
        model = SocialPlatformConfig
        fields = (
            'id',
            'platform',
            'is_enabled',
            'access_token',
            'access_token_secret',
            'page_or_account_id',
            'api_key',
            'api_secret',
            'bearer_token',
            'has_access_token',
            'has_access_token_secret',
            'has_api_key',
            'has_api_secret',
            'has_bearer_token',
            'extra_data',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'access_token': {'write_only': True, 'required': False},
            'access_token_secret': {'write_only': True, 'required': False},
            'api_key': {'write_only': True, 'required': False},
            'api_secret': {'write_only': True, 'required': False},
            'bearer_token': {'write_only': True, 'required': False},
        }


class SocialPostLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPostLog
        fields = (
            'id',
            'broadcast',
            'platform',
            'status',
            'external_post_id',
            'external_post_url',
            'error_message',
            'response_data',
            'created_at',
        )


class SocialBroadcastSerializer(serializers.ModelSerializer):
    logs = SocialPostLogSerializer(many=True, read_only=True)
    all_media_urls = serializers.ListField(child=serializers.URLField(), read_only=True)

    class Meta:
        model = SocialBroadcast
        fields = (
            'id',
            'title',
            'message',
            'link_url',
            'image_url',
            'media_urls',
            'all_media_urls',
            'target_platforms',
            'status',
            'scheduled_at',
            'published_at',
            'content_type',
            'object_id',
            'created_at',
            'updated_at',
            'logs',
        )


class SocialBroadcastCreateSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, help_text="The post message / caption to publish.")
    title = serializers.CharField(required=False, allow_blank=True, default="")
    link_url = serializers.URLField(required=False, allow_blank=True, default=None)
    image_url = serializers.URLField(required=False, allow_blank=True, default=None)
    media_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list,
        help_text="Optional list of image/media URLs for carousel/multi-image posts."
    )
    platforms = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=None,
        help_text="Optional list of platforms: ['facebook', 'instagram', 'twitter', 'linkedin', 'threads', 'tiktok']. If omitted, posts to all enabled."
    )
    scheduled_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text="Optional future datetime to schedule publishing. If omitted, publishes immediately."
    )


class SocialDirectMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialDirectMessage
        fields = (
            'id',
            'platform',
            'recipient_id',
            'sender_id',
            'message',
            'media_url',
            'direction',
            'status',
            'scheduled_at',
            'sent_at',
            'external_message_id',
            'conversation_id',
            'error_message',
            'response_data',
            'extra_data',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'direction',
            'status',
            'sent_at',
            'external_message_id',
            'conversation_id',
            'error_message',
            'response_data',
            'created_at',
            'updated_at',
        )


class SendMessageRequestSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(
        choices=SocialPlatformConfig.PLATFORM_CHOICES,
        help_text="Target platform: 'facebook', 'instagram', 'twitter', 'whatsapp', 'linkedin'."
    )
    recipient_id = serializers.CharField(
        max_length=255,
        required=True,
        help_text="Recipient ID (Page Scoped ID, IG User ID, Twitter User ID, Phone Number in E.164, or LinkedIn URN/vanity)."
    )
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Direct message text content."
    )
    media_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default=None,
        help_text="Optional URL to media file (image, video, document, audio)."
    )
    sender_id = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default=None,
        help_text="Optional custom sender ID or account ID."
    )
    scheduled_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        help_text="Optional future datetime to schedule sending. If omitted, sends immediately."
    )
    extra_params = serializers.DictField(
        required=False,
        default=dict,
        help_text="Optional platform-specific parameters (e.g. tag, template_name, quick_replies, media_type)."
    )

    def validate(self, attrs):
        message = attrs.get('message') or ''
        media_url = attrs.get('media_url')
        if not message.strip() and not media_url:
            raise serializers.ValidationError("Either 'message' or 'media_url' must be provided.")
        return attrs


class RescheduleRequestSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField(
        required=True,
        help_text="Future datetime to reschedule the broadcast or message."
    )
