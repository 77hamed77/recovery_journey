# community/admin.py

from django.contrib import admin
from .models import Post, Comment, Like, Follow, Conversation, Message, Report

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at', 'get_likes_count')
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('created_at', 'user')
    raw_id_fields = ('user',) # لتحسين أداء اختيار المستخدمين في لوحة المشرف

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'parent', 'get_likes_count')
    search_fields = ('content', 'user__username', 'post__title')
    list_filter = ('created_at', 'user', 'post')
    raw_id_fields = ('post', 'user', 'parent') # لتحسين أداء اختيار الأب في لوحة المشرف

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', 'created_at')
    list_filter = ('created_at', 'user', 'content_type')
    search_fields = ('user__username',)
    raw_id_fields = ('user',) # لتحسين أداء اختيار المستخدمين

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    list_filter = ('created_at', 'follower', 'followed')
    search_fields = ('follower__username', 'followed__username')
    raw_id_fields = ('follower', 'followed')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_participants', 'created_at', 'updated_at')
    filter_horizontal = ('participants',) # واجهة أفضل لاختيار المشاركين
    search_fields = ('participants__username',)

    def display_participants(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    display_participants.short_description = "المشاركون"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'created_at', 'is_read', 'content')
    list_filter = ('created_at', 'sender', 'is_read')
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('conversation', 'sender')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved', 'created_at', 'user', 'content_type')
    search_fields = ('user__username', 'description', 'content_object__title', 'content_object__content')
    actions = ['mark_resolved', 'mark_unresolved']
    raw_id_fields = ('user',)

    @admin.action(description="وضع علامة 'تم الحل' على البلاغات المحددة")
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, "تم وضع علامة 'تم الحل' على البلاغات بنجاح.", messages.SUCCESS)

    @admin.action(description="وضع علامة 'لم يتم الحل' على البلاغات المحددة")
    def mark_unresolved(self, request, queryset):
        queryset.update(is_resolved=False)
        self.message_user(request, "تم وضع علامة 'لم يتم الحل' على البلاغات بنجاح.", messages.SUCCESS)

