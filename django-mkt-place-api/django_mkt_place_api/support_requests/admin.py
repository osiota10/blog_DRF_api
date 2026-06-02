from django.contrib import admin
from .models import SupportRequest, SupportReply

class SupportReplyInline(admin.TabularInline):
    model = SupportReply
    extra = 1

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'subject', 'category', 'status', 'priority', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('ticket_id', 'subject', 'complaint', 'user__email', 'email')
    inlines = [SupportReplyInline]

@admin.register(SupportReply)
class SupportReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('message', 'ticket__ticket_id', 'author__email')
