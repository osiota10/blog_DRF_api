import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

class UserAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    label = models.CharField(max_length=100, help_text="e.g., 'Home', 'Office'")
    full_name = models.CharField(max_length=255)
    phone = PhoneNumberField()
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2, help_text="ISO alpha-2 country code")
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other default addresses for this user to False
            UserAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.label} - {self.full_name}"

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"


class VerificationOTP(models.Model):
    OTP_TYPES = [
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
        ('password_reset', 'Password Reset'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_otps'
    )
    otp = models.CharField(max_length=100, unique=True)
    otp_type = models.CharField(max_length=50, choices=OTP_TYPES)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.user} - {self.otp_type} - {self.otp}"

    class Meta:
        verbose_name = "Verification OTP"
        verbose_name_plural = "Verification OTPs"
