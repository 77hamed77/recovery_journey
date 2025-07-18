# users/urls.py
from django.urls import path
from .views import register_view

urlpatterns = [
    path('register/', register_view, name='register'),
    # سنضيف روابط الدخول والخروج لاحقاً
]