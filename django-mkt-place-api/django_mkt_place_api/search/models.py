import uuid
from django.db import models

class FailedIndexAttempt(models.Model):
    OP_CHOICES = [
        ('index', 'Index'),
        ('remove', 'Remove'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.UUIDField(db_index=True)
    operation = models.CharField(max_length=20, choices=OP_CHOICES)
    error = models.TextField(help_text="Debug error details")
    attempts = models.PositiveSmallIntegerField(default=1, help_text="Retry counter")
    resolved = models.BooleanField(default=False, help_text="Flags completed retries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Failed {self.operation} attempt for {self.product_id} (Resolved: {self.resolved})"
