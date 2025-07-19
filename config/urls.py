# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('companion/', include('companion.urls')), # <--- أضف هذا السطر
    path('', include('journal.urls')),
]