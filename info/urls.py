# info/urls.py

from django.urls import path
from . import views

app_name = 'info'

urlpatterns = [
    # صفحات عامة
    path('about/', views.about_view, name='about'),
    path('privacy/', views.privacy_view, name='privacy'),

    # صفحة تواصل المستخدم مع الطبيب
    path('contact/', views.contact_view, name='contact'),
    path('contact/history/', views.contact_history_view, name='contact_history'),

    # إدارة رسائل التواصل - للطبيب النفسي فقط
    path(
        'admin/messages/',
        views.admin_messages_list,
        name='admin_messages_list'
    ),
    path(
        'admin/messages/<int:pk>/',
        views.admin_message_detail,
        name='admin_message_detail'
    ),

    # عرض الموارد
    path('resources/', views.resources_list_view, name='resources_list'),
    path('resources/<int:pk>/', views.resource_detail_view, name='resource_detail'),

    # إدارة الموارد (للطبيب النفسي فقط)
    path(
        'resources/create/',
        views.resource_create_view,
        name='resource_create'
    ),
    path(
        'resources/<int:pk>/edit/',
        views.resource_edit_view,
        name='resource_edit'
    ),
    path(
        'resources/<int:pk>/delete/',
        views.resource_confirm_delete_view,
        name='resource_confirm_delete'
    ),
    path('contact/history/', views.contact_history_view, name='contact_history'),
# Dashboard للطبيب النفسي
    path(
        'admin/dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    # إدارة رسائل التواصل
    path('admin/messages/',      views.admin_messages_list,   name='admin_messages_list'),
    path('admin/messages/<int:pk>/', views.admin_message_detail, name='admin_message_detail'),
]