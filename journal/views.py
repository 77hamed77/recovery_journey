# journal/views.py

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .models import JournalEntry, UserAchievement
from .achievements_engine import check_and_award_achievements, get_achievements_data, get_user_streak

def get_character_level(unlocked_ids):
    streak_achievements = [id for id in unlocked_ids if "STREAK_UNLOCKED" in id]
    # كل إنجاز سلسلة يرفع المستوى درجة
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
    
    # --- التعامل مع طلبات POST (عندما يحفظ المستخدم يومياته عبر HTMX) ---
    if request.method == 'POST':
        content = request.POST.get('daily_entry', '').strip()
        
        # تحقق إذا كان المستخدم قد كتب بالفعل اليوم أو المحتوى فارغ
        if JournalEntry.objects.filter(user=user, entry_date=today).exists() or not content:
            # لا تفعل شيئًا إذا حاول الإرسال مرة أخرى أو أرسل محتوى فارغ
            return HttpResponse(status=204) # 204 No Content

        # حفظ اليومية الجديدة
        entry_time = timezone.now() # حفظ الوقت الحالي للتحقق من الإنجازات الخاصة
        JournalEntry.objects.create(user=user, content=content, entry_date=today, created_at=entry_time)

        # -->> هنا نستدعي محرك الإنجازات <<--
        newly_unlocked = check_and_award_achievements(user, entry_time)
        # تجهيز استجابة HTMX
        response = render(request, 'journal/partials/daily_entry_success.html')
        
        # إذا كانت هناك إنجازات جديدة، أرسلها إلى الواجهة الأمامية عبر هيدر خاص
        if newly_unlocked:
            trigger_data = {'achievementsUnlocked': newly_unlocked}
            response['HX-Trigger'] = json.dumps(trigger_data)
            
        return response

    # --- منطق طلبات GET (عند عرض الصفحة لأول مرة) ---
    
    # حساب الأيام المنقضية (العداد الرئيسي)
    days_passed = (today - user.date_joined.date()).days

    # جلب الإنجازات التي يملكها المستخدم بالفعل لعرضها
    unlocked_achievements_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))
    all_achievements_data = get_achievements_data()
    
    context = {
        'days_passed': days_passed,
        'target_days': 90, # يمكنك جعل هذا الرقم ديناميكياً من الإعدادات لاحقاً
        'streak': get_user_streak(user),
        'already_written_today': JournalEntry.objects.filter(user=user, entry_date=today).exists(),
        
        # تمرير بيانات الإنجازات للواجهة الأمامية بأمان
        'all_achievements_data_json': all_achievements_data,
        'unlocked_achievements_ids_json': list(unlocked_achievements_ids),
        
        'character_level': get_character_level(unlocked_achievements_ids),

    }
    
    return render(request, 'journal/dashboard.html', context)