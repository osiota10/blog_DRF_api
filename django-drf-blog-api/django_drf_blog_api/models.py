from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.html import strip_tags
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Author(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author_profile')
    role = models.CharField(max_length=100, default='Author', blank=True, null=True)

    def __str__(self):
        return f"{self.user} ({self.role})"


class MagazineSeries(models.Model):
    series_number = models.CharField(max_length=100, help_text="e.g. Series 41")
    edition_code = models.CharField(max_length=100, help_text="e.g. VOL. 41 • NO. 01")
    date = models.CharField(max_length=100, help_text="e.g. January 2026")
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    badge = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. CURRENT EDITION")
    cover_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, blank=True, null=True, related_name='magazine_covers'
    )
    cover_image_url = models.URLField(blank=True, null=True, help_text="Direct cover image URL")
    editorial_summary = models.TextField(blank=True, null=True)
    lead_stories = models.JSONField(default=list, blank=True, help_text="List of lead story headlines")
    slug = models.SlugField(max_length=250, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def cover_image(self):
        if self.cover_media:
            return self.cover_media.url
        return self.cover_image_url

    def __str__(self):
        return f"{self.series_number} - {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Magazine Series"
        verbose_name_plural = "Magazine Series"


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Text', config_name='extends')
    excerpt = models.TextField(blank=True, null=True, help_text="Short summary of the post")
    read_time = models.PositiveIntegerField(default=0, help_text="Estimated read time in minutes")
    featured_media = models.ForeignKey(
        'media_library.MediaAsset', on_delete=models.SET_NULL, blank=True, null=True, related_name='featured_posts',
        help_text="Linked MediaAsset from media_library"
    )
    featured_image_url = models.URLField(blank=True, null=True, help_text="Direct URL to external featured image")
    featured_image_url_caption = models.TextField(
        blank=True, null=True, help_text="Caption or credit text for the featured image"
    )
    pub_date = models.DateTimeField(default=timezone.now, help_text="Publication date of the post")
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        Author, related_name='posts', on_delete=models.CASCADE, null=True, blank=True)
    magazine_series = models.ForeignKey(
        MagazineSeries, on_delete=models.SET_NULL, blank=True, null=True, related_name='posts',
        help_text="Linked Magazine Series"
    )

    @property
    def featured_image(self):
        """Returns the media asset URL if available, otherwise external image URL."""
        if self.featured_media:
            return self.featured_media.url
        return self.featured_image_url
    category = models.ForeignKey(
        Category, related_name='post_category', on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.ManyToManyField(
        Tag, related_name='post_tag', blank=True)
    keywords = models.ManyToManyField(
        Keyword, related_name='post_keyword', blank=True)
    slug = models.SlugField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.title

    def safe_post_content_html(self):
        return strip_tags(self.content)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comment_user',
                             on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.post} at {self.created_at}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like by {self.user} on {self.content_object} at {self.created_at}"
