from rest_framework import serializers
from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog


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

    class Meta:
        model = SocialBroadcast
        fields = (
            'id',
            'title',
            'message',
            'link_url',
            'image_url',
            'target_platforms',
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
    platforms = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=None,
        help_text="Optional list of platforms: ['facebook', 'instagram', 'twitter', 'linkedin']. If omitted, posts to all enabled."
    )
