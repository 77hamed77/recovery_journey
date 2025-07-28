# community/urls.py

from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # المنشورات
    path('', views.post_list_view, name='post_list'),
    path('post/new/', views.post_create_view, name='post_create'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit_view, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete_view, name='post_delete'),

    # التعليقات
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/reply/', views.add_reply_to_comment, name='add_reply_to_comment'),
    
    # الإعجابات (المسار الجديد العام)
    path('like/<int:content_type_id>/<int:object_id>/', views.like_toggle_view, name='like_toggle'),

    # المتابعة
    path('follow/<int:user_id>/', views.follow_toggle_view, name='follow_toggle'),

    # الرسائل الخاصة
    path('inbox/', views.inbox_view, name='inbox'),
    path('conversation/start/<int:user_id>/', views.start_new_conversation_view, name='start_new_conversation'),
    path('conversation/<int:pk>/', views.conversation_detail_view, name='conversation_detail'),
    path('conversation/<int:pk>/send/', views.send_message_view, name='send_message'),
    
    # الإبلاغ عن المحتوى
    path('report/<int:content_type_id>/<int:object_id>/', views.report_content_view, name='report_content'),

    # إرشادات المجتمع
    path('guidelines/', views.guidelines_view, name='guidelines'),
]

