# journal/views.py

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .models import JournalEntry, UserAchievement
from .achievements_engine import check_and_award_achievements, get_achievements_data, get_user_streak

def get_character_level(unlocked_ids: set) -> int:
    """يحسب مستوى الشخصية بناءً على إنجازات السلاسل المحققة."""
    streak_achievements = [ach_id for ach_id in unlocked_ids if "STREAK_UNLOCKED" in ach_id]
    return len(streak_achievements)

@login_required
def dashboard_view(request):
    """
    عرض وإدارة لوحة التحكم الخاصة بالمستخدم.
    - طلبات GET: تعرض الصفحة مع البيانات الحالية.
    - طلبات POST (عبر HTMX): تحفظ يومية جديدة وتتحقق من الإنجازات.
    """
    user = request.user
    today = timezone.localdate()
    
    # التعامل مع طلبات POST (عندما يحفظ المستخدم يومياته عبر HTMX)
    if request.method == 'POST':
        content = request.POST.get('daily_entry', '').strip()
        
        if JournalEntry.objects.filter(user=user, entry_date=today).exists() or not content:
            return HttpResponse(status=204)  # 204 No Content

        entry_time = timezone.now()
        JournalEntry.objects.create(user=user, content=content, entry_date=today, created_at=entry_time)

        # -->> استدعاء محرك الإنجازات مع تمرير محتوى اليومية <<--
        newly_unlocked = check_and_award_achievements(user, entry_time, content)
        
        response = render(request, 'journal/partials/daily_entry_success.html')
        
        if newly_unlocked:
            trigger_data = {'achievementsUnlocked': newly_unlocked}
            response['HX-Trigger'] = json.dumps(trigger_data)
            
        return response

    # منطق طلبات GET (عند عرض الصفحة لأول مرة)
    days_passed = (today - user.date_joined.date()).days

    unlocked_achievements_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))
    all_achievements_data = get_achievements_data()
    
    context = {
        'days_passed': days_passed,
        'target_days': 90,
        'streak': get_user_streak(user),
        'already_written_today': JournalEntry.objects.filter(user=user, entry_date=today).exists(),
        
        # تمرير بيانات الإنجازات الكاملة للواجهة الأمامية بأمان
        'all_achievements_data_json': all_achievements_data,
        
        # حساب مستوى الشخصية
        'character_level': get_character_level(unlocked_achievements_ids),
    }
    
    return render(request, 'journal/dashboard.html', context)