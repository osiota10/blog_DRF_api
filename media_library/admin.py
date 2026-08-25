from django.contrib import admin
from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'media_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('media_type', 'uploaded_at')
    search_fields = ('title', 'alt_text', 'caption')
