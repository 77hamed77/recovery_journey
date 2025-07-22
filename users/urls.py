from django.urls import path
from . import views # استيراد جميع الـ views من ملف views.py

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('set-start-date/', views.set_start_date_view, name='set_start_date'), # مسار لتحديد تاريخ البدء
    path('settings/delete/', views.delete_account_view, name='delete_account'), # مسار لحذف الحساب
    path('settings/password/', views.password_change_view, name='password_change'), # مسار لتغيير كلمة المرور
    path('my-journals/', views.my_journal_view, name='my_journal'), # مسار لعرض اليوميات
]

