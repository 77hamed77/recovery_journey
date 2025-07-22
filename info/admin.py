# info/admin.py
from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'url', 'file')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'created_by')