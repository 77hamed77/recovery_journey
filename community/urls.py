# community/urls.py

from django.urls import path
from . import views

app_name = 'community' # تحديد اسم التطبيق لتجنب تعارض الأسماء

urlpatterns = [
    path('', views.post_list_view, name='post_list'),
    path('new/', views.post_create_view, name='post_create'),
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('<int:post_id>/edit/', views.post_edit_view, name='post_edit'),
    path('<int:post_id>/delete/', views.post_delete_view, name='post_delete'),
]

