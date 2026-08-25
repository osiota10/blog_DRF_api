from rest_framework import serializers
from .models import MediaAsset


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField()
    thumbnail_url = serializers.ReadOnlyField(source='get_thumbnail_url')

    class Meta:
        model = MediaAsset
        fields = [
            'id',
            'title',
            'alt_text',
            'caption',
            'media_type',
            'file',
            'external_url',
            'url',
            'thumbnail_url',
            'uploaded_by',
            'uploaded_at',
            'updated_at',
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at', 'updated_at']
