from rest_framework import serializers
from .models import SocialPlatformConfig, SocialBroadcast, SocialPostLog


class SocialPlatformConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPlatformConfig
        fields = (
            'id',
            'platform',
            'is_enabled',
            'access_token',
            'page_or_account_id',
            'api_key',
            'bearer_token',
            'extra_data',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'access_token': {'write_only': True},
            'api_key': {'write_only': True},
            'bearer_token': {'write_only': True},
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
