from django.contrib import admin
from .models import FailedIndexAttempt

@admin.register(FailedIndexAttempt)
class FailedIndexAttemptAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'operation', 'attempts', 'resolved', 'created_at')
    list_filter = ('operation', 'resolved')
    search_fields = ('product_id', 'error')
