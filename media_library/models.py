from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class MediaAsset(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'
        AUDIO = 'audio', 'Audio'
        DOCUMENT = 'document', 'Document'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Accessibility text (primarily for images)"
    )
    caption = models.TextField(blank=True, null=True)
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.IMAGE
    )

    # resource_type='auto' allows Cloudinary to accept images, videos, PDFs, etc.
    file = CloudinaryField(
        'media',
        resource_type='auto',
        folder='media_library',
        blank=True,
        null=True
    )

    # Direct URL fallback (for embedded YouTube/Vimeo links, external CDNs, etc.)
    external_url = models.URLField(
        blank=True,
        null=True,
        help_text="Fallback for external links, YouTube/Vimeo embeds, or third-party CDNs"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_media'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Media Asset'
        verbose_name_plural = 'Media Assets'

    @property
    def url(self):
        """Returns the Cloudinary file URL or the external link."""
        if self.file:
            return self.file.url
        return self.external_url

    def get_thumbnail_url(self):
        """Generates a responsive preview thumbnail for Cloudinary assets."""
        if not self.file:
            return self.external_url

        # If it's a video, Cloudinary automatically can generate a .jpg frame thumbnail
        if self.media_type == self.MediaType.VIDEO:
            return self.file.build_url(resource_type='video', format='jpg', width=300, crop='fill')

        # For images, auto-optimize and resize
        return self.file.build_url(width=300, crop='fill', fetch_format='auto', quality='auto')

    def __str__(self):
        return self.title or self.url
