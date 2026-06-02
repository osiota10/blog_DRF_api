from django.db import models
from django.conf import settings

class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(null=True, blank=True, help_text="Contextual deep-links/payload details")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    is_read = models.BooleanField(default=False, db_index=True)
    action_url = models.CharField(max_length=500, null=True, blank=True)
    action_text = models.CharField(max_length=100, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user})"


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preference'
    )
    push_order_updates = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=True)
    sms_delivery_alerts = models.BooleanField(default=True)
    vendor_new_orders = models.BooleanField(default=True)
    vendor_low_stock = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification Preferences for {self.user}"


class PushToken(models.Model):
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_tokens'
    )
    token = models.CharField(max_length=500, unique=True, db_index=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} token for {self.user}"


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('push', 'Push'),
        ('sms', 'SMS'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.channel} log to {self.user} - Status: {self.status}"
