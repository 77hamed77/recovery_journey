# companion/admin.py
from django.contrib import admin
from .models import ChatMessage

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_text', 'response_text', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('message_text', 'response_text')

admin.site.register(ChatMessage, ChatMessageAdmin)