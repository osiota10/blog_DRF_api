from django.contrib import admin
from .models import UserAddress, VerificationOTP

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'full_name', 'city', 'country', 'is_default')
    list_filter = ('is_default', 'country')
    search_fields = ('user__email', 'full_name', 'city')

@admin.register(VerificationOTP)
class VerificationOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_type', 'otp', 'expires_at', 'is_used')
    list_filter = ('otp_type', 'is_used')
    search_fields = ('user__email', 'otp')
