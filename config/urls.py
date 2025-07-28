# config/urls.py

"""
config URL Configuration

The `urlpatterns` list routes URLs to views. 
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# استيراد صفحة الهبوط للزائرين
from info.views import landing_view

urlpatterns = [
    # الصفحة الرئيسية: صفحة هبوط أو إعادة توجيه للمسجلين
    path('', landing_view, name='landing'),

    # لوحة إدارة Django
    path('admin/', admin.site.urls),

    # تطبيق المستخدمين (تسجيل/دخول/مستخدمين)
    path('users/', include('users.urls')),
    path(
    'users/',
    include(
        ('users.urls', 'users'),  # tuple: (module, app_name)
        namespace='users')
    ),
    # تطبيق الرفيق (chatbot)
    path('companion/', include('companion.urls')),

    # تطبيق الأهداف
    path('goals/', include('goals.urls')),
    
    # تطبيق المجتمع
    path('community/', include('community.urls')),

    # صفحات ثانوية ومعلومات عامة
    path('info/', include('info.urls', namespace='info')),

    # تطبيق اليوميات (يشمل داشبورد المستخدم وغيرها)
    path('journal/', include('journal.urls', namespace='journal')),
]

# أثناء التطوير، خدم الملفات الثابتة وملفات الوسائط
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
