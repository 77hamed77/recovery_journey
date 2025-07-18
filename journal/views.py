# journal/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required # هذا السطر يضمن أن المستخدم يجب أن يكون مسجلاً للدخول
def dashboard_view(request):
    user = request.user
    start_date = user.date_joined # تاريخ بداية الرحلة هو تاريخ إنشاء الحساب
    now = timezone.now()
    
    # حساب الفارق الزمني وإضافة 1 لأن اليوم الأول يُحسب كيوم 1
    days_passed = (now - start_date).days + 1
    
    context = {
        'days_passed': days_passed,
        'target_days': 90,
    }
    return render(request, 'journal/dashboard.html', context)