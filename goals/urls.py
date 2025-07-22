# goals/urls.py

from django.urls import path
from . import views

app_name = 'goals' # Namespace for the goals app

urlpatterns = [
    # List all goals for the current user
    path('', views.goals_list, name='goals_list'),
    
    # View details of a single goal
    path('<int:pk>/', views.goal_detail, name='goal_detail'),
    
    # Create a new goal
    path('create/', views.goal_create, name='goal_create'),
    
    # Edit an existing goal
    path('<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    
    # Confirm deletion of a goal
    path('<int:pk>/delete/', views.goal_confirm_delete, name='goal_confirm_delete'),
]

