from django.urls import path
from . import views

app_name = 'journal'  # تعريف مساحة الأسماء

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('entries/', views.journal_entries_view, name='journal_entries'),
    path('goals/', views.goals_view, name='goals_list'),
    path('companion/', views.companion_view, name='companion'),
    path('add/', views.add_entry_view, name='add_entry'),
    path('edit/<int:entry_id>/', views.edit_entry_view, name='edit_entry'),
    path('delete/<int:entry_id>/', views.delete_entry_view, name='delete_entry'),
    path('achievements/', views.achievements_view, name='achievements'),
]