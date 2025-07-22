# journal/urls.py

from django.urls import path
from . import views

app_name = 'journal' # Namespace for the journal app

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('my-journals/', views.my_journals_view, name='my_journals'), # <-- إضافة هذا السطر
    path('edit/<int:entry_id>/', views.edit_journal_entry, name='edit_journal_entry'), # <-- إضافة مسار التعديل
    path('delete/<int:entry_id>/', views.delete_journal_entry, name='delete_journal_entry'), # <-- إضافة مسار الحذف
    # ... أضف هنا أي مسارات أخرى لتطبيق اليوميات
]

