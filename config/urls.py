# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')), # أي رابط يبدأ بـ /accounts/ سيذهب إلى users.urls
    path('', include('journal.urls')), # أي رابط فارغ (الصفحة الرئيسية) سيذهب إلى journal.urls
]