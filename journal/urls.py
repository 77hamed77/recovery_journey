from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('my_journal/', views.journal_entries_view, name='my_journal'),
    path('goals/', views.goals_view, name='goals'),
    path('companion/', views.companion_view, name='companion'),
    path('add_entry/', views.add_entry_view, name='add_entry'),
    path('edit_entry/<int:entry_id>/', views.edit_entry_view, name='edit_entry'),
    path('delete_entry/<int:entry_id>/', views.delete_entry_view, name='delete_entry'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('relapse_support/', views.relapse_support_view, name='relapse_support'),
]