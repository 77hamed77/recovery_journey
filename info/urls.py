# info/urls.py

from django.urls import path
from . import views

app_name = 'info' # Namespace for the info app

urlpatterns = [
    # General info pages
    path('about/', views.about_view, name='about'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('contact/', views.contact_view, name='contact'),

    # Resource management pages (publicly viewable, but editable by superuser)
    path('resources/', views.resources_list_view, name='resources_list'),
    path('resources/<int:pk>/', views.resource_detail_view, name='resource_detail'),
    
    # Superuser-only resource management
    path('resources/create/', views.resource_create_view, name='resource_create'),
    path('resources/<int:pk>/edit/', views.resource_edit_view, name='resource_edit'),
    path('resources/<int:pk>/delete/', views.resource_confirm_delete_view, name='resource_confirm_delete'),
]

