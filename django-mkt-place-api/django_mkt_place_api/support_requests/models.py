import uuid
from django.db import models
from django.conf import settings

class SupportRequest(models.Model):
    CATEGORY_CHOICES = [
        ('order_issue', 'Order Issue'),
        ('payment', 'Payment / Billing'),
        ('refund', 'Refund / Return'),
        ('shipping', 'Shipping & Delivery'),
        ('general', 'General Inquiry'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting on Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    ticket_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_requests'
    )
    name = models.CharField(max_length=255, null=True, blank=True, help_text="For guest submissions")
    email = models.EmailField(null=True, blank=True, help_text="For guest submissions")
    subject = models.CharField(max_length=255)
    complaint = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_requests'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_support_tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.subject} ({self.status})"


class SupportReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportRequest, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="If True, this reply is only visible to admin/staff members."
    )
    attachments = models.JSONField(default=list, blank=True, help_text="List of uploaded file URLs")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Support Replies"

    def __str__(self):
        role = "Internal" if self.is_internal else "Public"
        return f"Reply on {self.ticket.ticket_id} by {self.author} ({role})"
