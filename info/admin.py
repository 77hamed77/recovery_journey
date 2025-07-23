# info/admin.py

from django.contrib import admin
from .models import Resource, ContactMessage

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'url', 'file')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'created_by')
    ordering = ('-created_at',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'created_at', 'is_replied')
    search_fields = ('subject', 'message', 'reply', 'user__username')
    list_filter = ('created_at', 'replied_at', 'user', 'replied_by')
    readonly_fields = ('created_at', 'replied_at', 'user', 'subject', 'message')

    fieldsets = (
        (None, {
            'fields': ('user', 'subject', 'message')
        }),
        ('الرد من الطبيب النفسي', {
            'fields': ('reply', 'replied_by', 'replied_at'),
            'description': 'أضف ردك هنا وسيُخزن تاريخه ومن قام بالرد تلقائيًا.'
        }),
    )

    def is_replied(self, obj):
        return obj.is_replied
    is_replied.boolean = True
    is_replied.short_description = 'تم الرد؟'
