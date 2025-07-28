# community/urls.py

from django.urls import path
from . import views
from django.contrib.contenttypes.models import ContentType
from community.models import Post, Comment

app_name = 'community' # تحديد اسم التطبيق لتجنب تعارض الأسماء

urlpatterns = [
    # مسارات المنشورات الأساسية
    path('', views.post_list_view, name='post_list'),
    path('new/', views.post_create_view, name='post_create'),
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('<int:post_id>/edit/', views.post_edit_view, name='post_edit'),
    path('<int:post_id>/delete/', views.post_delete_view, name='post_delete'),

    # مسارات الإعجابات
    path('like/post/<int:object_id>/', views.like_content_view, name='like_post', 
         kwargs={'content_type_id': ContentType.objects.get_for_model(Post).id}),
    path('like/comment/<int:object_id>/', views.like_content_view, name='like_comment',
         kwargs={'content_type_id': ContentType.objects.get_for_model(Comment).id}),
    
    # مسارات المتابعة
    path('follow/<int:user_id>/', views.follow_user_view, name='follow_user'),

    # مسارات الرسائل الخاصة
    path('inbox/', views.inbox_view, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('start-chat/<int:user_id>/', views.start_new_conversation_view, name='start_chat'),

    # مسارات الإبلاغ عن المحتوى
    path('report/post/<int:object_id>/', views.report_content_view, name='report_post',
         kwargs={'content_type_id': ContentType.objects.get_for_model(Post).id}),
    path('report/comment/<int:object_id>/', views.report_content_view, name='report_comment',
         kwargs={'content_type_id': ContentType.objects.get_for_model(Comment).id}),

    # مسارات الصفحات الثابتة للمجتمع
    path('guidelines/', views.community_guidelines_view, name='community_guidelines'),
]

