# community/admin.py

from django.contrib import admin
from .models import Post, Comment, Like, Follow, Conversation, Message, Report

# لتسجيل نماذجك في لوحة المشرف

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'get_likes_count') # أضف get_likes_count هنا
    search_fields = ('title', 'content', 'user__username')
    list_filter = ('created_at',)
    raw_id_fields = ('user',) # لتحسين أداء اختيار المستخدم في حقول الفورين كي


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'parent', 'get_likes_count') # أضف get_likes_count هنا
    search_fields = ('content', 'user__username')
    list_filter = ('created_at', 'post')
    raw_id_fields = ('post', 'user', 'parent')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_object', 'created_at') # 'content_object' هو الاسم الصحيح
    list_filter = ('created_at', 'content_type')
    raw_id_fields = ('user', 'content_type')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'followed_user', 'created_at') # 'user' و 'followed_user' هما الصحيحان
    search_fields = ('user__username', 'followed_user__username')
    list_filter = ('created_at', 'user', 'followed_user') # 'user' و 'followed_user' هما الصحيحان
    raw_id_fields = ('user', 'followed_user') # 'user' و 'followed_user' هما الصحيحان


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('display_participants', 'created_at', 'updated_at')
    filter_horizontal = ('participants',) # طريقة أفضل لعرض حقل ManyToManyField
    search_fields = ('participants__username',)
    list_filter = ('created_at', 'updated_at')

    def display_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    display_participants.short_description = "المشاركون"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'created_at', 'is_read')
    list_filter = ('created_at', 'is_read', 'sender')
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('conversation', 'sender')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'reported_object_type', 'reported_object', 'reason', 'is_resolved', 'created_at') # 'reported_object' هو الصحيح
    list_filter = ('created_at', 'reason', 'is_resolved', 'content_type')
    search_fields = ('user__username', 'description', 'reported_object_id')
    raw_id_fields = ('user', 'content_type')

