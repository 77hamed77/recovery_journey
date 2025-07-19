# users/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # مسار لصفحة إنشاء حساب جديد
    path('register/', views.register_view, name='register'),
    
    # مسار لصفحة تسجيل الدخول
    path('login/', views.login_view, name='login'),
    
    # مسار لمعالجة طلب تسجيل الخروج
    path('logout/', views.logout_view, name='logout'),
    
    # مسار لصفحة الإعدادات الخاصة بالمستخدم
    path('settings/', views.settings_view, name='settings'),
]