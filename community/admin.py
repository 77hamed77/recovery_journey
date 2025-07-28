# community/admin.py

from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('created_at', 'user')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'content')
    search_fields = ('content', 'user__username', 'post__title')
    list_filter = ('created_at', 'user', 'post')

