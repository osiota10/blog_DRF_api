from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SocialPlatformConfig(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook Page'),
        ('instagram', 'Instagram Business'),
        ('twitter', 'X / Twitter'),
        ('linkedin', 'LinkedIn'),
        ('threads', 'Threads'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp Business'),
    ]
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=True)
    access_token = models.TextField(blank=True, null=True, help_text="OAuth access token (Leave blank to use .env)")
    refresh_token = models.TextField(blank=True, null=True)
    page_or_account_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Page ID, Instagram Account ID, or LinkedIn Org/Person ID"
    )
    api_key = models.CharField(max_length=255, blank=True, null=True, help_text="Twitter API Consumer Key")
    api_secret = models.CharField(max_length=255, blank=True, null=True, help_text="Twitter API Consumer Secret")
    access_token_secret = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Twitter OAuth 1.0a Access Token Secret (required with API key/secret and access token)"
    )
    bearer_token = models.TextField(blank=True, null=True, help_text="Twitter Bearer Token / OAuth 2.0 User Access Token")
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_platform_display()} ({'Enabled' if self.is_enabled else 'Disabled'})"

    class Meta:
        ordering = ['platform']
        verbose_name = "Social Platform Configuration"
        verbose_name_plural = "Social Platform Configurations"


class SocialBroadcast(models.Model):
    """
    Represents a unified broadcast event targeting one or more social media platforms.
    Can be initiated directly via API or linked generically to any model (Post, Product, Event, etc.).
    Supports immediate publishing or scheduled future publication.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('publishing', 'Publishing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(help_text="Primary broadcast message or caption")
    link_url = models.URLField(max_length=500, blank=True, null=True, help_text="Target article / page URL to share")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Image attachment URL")
    media_urls = models.JSONField(default=list, blank=True, help_text="List of media/image URLs for carousel/multi-image posts")
    target_platforms = models.JSONField(default=list, blank=True, help_text="Platforms targeted for this broadcast")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="Future date/time to publish this broadcast. If None, published immediately.")
    published_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when broadcast was actually published to platforms.")

    # Generic relation to any source model (Post, Product, Event, Listing, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def all_media_urls(self) -> list:
        urls = []
        if self.image_url:
            urls.append(self.image_url)
        if self.media_urls and isinstance(self.media_urls, list):
            for u in self.media_urls:
                if u and u not in urls:
                    urls.append(u)
        return urls

    def __str__(self):
        return f"Broadcast #{self.id} [{self.status}]: {self.title or self.message[:30]}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Social Broadcast"
        verbose_name_plural = "Social Broadcasts"


class SocialPostLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('published', 'Published'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    broadcast = models.ForeignKey(SocialBroadcast, on_delete=models.CASCADE, related_name='logs')
    platform = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_post_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID returned by platform")
    external_post_url = models.URLField(max_length=500, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    response_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform.capitalize()} - {self.status} (Broadcast #{self.broadcast_id})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Social Post Log"
        verbose_name_plural = "Social Post Logs"


class SocialDirectMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    DIRECTION_CHOICES = [
        ('outbound', 'Outbound (Sent)'),
        ('inbound', 'Inbound (Received)'),
    ]
    platform = models.CharField(max_length=30, choices=SocialPlatformConfig.PLATFORM_CHOICES)
    recipient_id = models.CharField(max_length=255, help_text="Platform user ID, phone number, or chat handle")
    sender_id = models.CharField(max_length=255, blank=True, null=True, help_text="Sender ID or Page/Account ID")
    message = models.TextField(help_text="Message text content")
    media_url = models.URLField(max_length=500, blank=True, null=True, help_text="Optional media attachment URL")
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='outbound')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="Future date/time to send this message. If None, sent immediately.")
    sent_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when message was actually delivered to platform.")
    external_message_id = models.CharField(max_length=255, blank=True, null=True, help_text="Message ID returned by platform")
    conversation_id = models.CharField(max_length=255, blank=True, null=True, help_text="Conversation or Thread ID")
    error_message = models.TextField(blank=True, null=True)
    response_data = models.JSONField(default=dict, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def all_media_urls(self) -> list:
        urls = []
        if self.image_url:
            urls.append(self.image_url)
        if self.media_urls and isinstance(self.media_urls, list):
            for u in self.media_urls:
                if u and u not in urls:
                    urls.append(u)
        return urls

    def __str__(self):
        return f"[{self.platform.upper()}] DM to {self.recipient_id} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Social Direct Message"
        verbose_name_plural = "Social Direct Messages"

