# companion/admin.py

from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ChatMessage model.
    Displays user, message, response, and timestamp in the list view.
    Allows searching by message and response content.
    Filters by user and timestamp.
    """
    list_display = ('user', 'message', 'response', 'timestamp') # تم تصحيح أسماء الحقول هنا
    search_fields = ('message', 'response')
    list_filter = ('user', 'timestamp')
    readonly_fields = ('user', 'timestamp') # جعل هذه الحقول للقراءة فقط في لوحة المشرف

