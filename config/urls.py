"""
config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# استيراد view لوحة التحكم مباشرة إذا كانت هي الصفحة الرئيسية
from journal.views import dashboard_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    # تضمين مسارات تطبيق المستخدمين
    path('users/', include('users.urls')), 
    # تضمين مسارات تطبيق الرفيق (chatbot)
    path('companion/', include('companion.urls')),
    path('goals/', include('goals.urls')),
    path('info/', include('info.urls')),
    # تضمين مسارات تطبيق اليوميات (إذا كان journal.urls يحتوي على أكثر من مجرد لوحة التحكم)
    # إذا كانت لوحة التحكم هي الوحيدة في journal.views، يمكن استيرادها مباشرة كما هو الحال الآن.
    path('journal/', include('journal.urls')), # أضف هذا إذا كان journal.urls يحتوي على مسارات أخرى غير dashboard
    
    # المسار الافتراضي للموقع (الصفحة الرئيسية)
    path('', dashboard_view, name='dashboard'), 
]

# إضافة مسارات الملفات الثابتة في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # إذا كان لديك ملفات وسائط

