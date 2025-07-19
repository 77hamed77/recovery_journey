# journal/achievements_engine.py

import json
from pathlib import Path
from datetime import date, timedelta, datetime
from django.conf import settings
from django.contrib.auth.models import User
from .models import JournalEntry, UserAchievement

# تحديد مسار ملف الإنجازات
ACHIEVEMENTS_FILE = Path(settings.BASE_DIR) / "static/data/achievements.json"

def get_achievements_data():
    """يقرأ ويعيد بيانات الإنجازات من ملف JSON."""
    with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_user_streak(user: User) -> int:
    """
    دالة محسّنة لحساب عدد الأيام المتتالية التي كتب فيها المستخدم.
    """
    # جلب تواريخ الإدخالات الفريدة (distinct) ومرتبة
    entry_dates = list(user.journalentry_set.order_by('-entry_date').values_list('entry_date', flat=True).distinct())
    
    if not entry_dates:
        return 0

    streak = 0
    today = date.today()
    
    # تحقق إذا كانت آخر يومية هي اليوم أو الأمس لبدء العد
    if entry_dates[0] == today or entry_dates[0] == today - timedelta(days=1):
        streak = 1
        # ابدأ العد من ثاني يومية
        for i in range(len(entry_dates) - 1):
            # إذا كان الفارق بين اليومية الحالية والسابقة هو يوم واحد بالضبط
            if entry_dates[i] - entry_dates[i+1] == timedelta(days=1):
                streak += 1
            else:
                # انكسرت سلسلة الأيام المتتالية
                break
    return streak

def check_and_award_achievements(user: User, entry_time: datetime) -> list:
    """
    الوظيفة الرئيسية التي تتحقق من جميع الإنجازات للمستخدم بعد حفظ إدخال جديد.
    وترجع قائمة بالإنجازات الجديدة التي تم فتحها.
    
    Args:
        user: كائن المستخدم الحالي.
        entry_time: وقت حفظ اليومية الجديدة للتحقق من الإنجازات الخاصة.
        
    Returns:
        قائمة من القواميس، حيث يمثل كل قاموس إنجازًا جديدًا تم فتحه.
    """
    all_achievements_data = get_achievements_data()
    achievements = all_achievements_data['achievements']
    
    # جلب جميع الإنجازات التي يملكها المستخدم بالفعل لتجنب التكرار
    unlocked_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))
    newly_unlocked = []

    def award_achievement(ach_details):
        """دالة مساعدة لتسجيل إنجاز جديد وإضافته إلى قائمة النتائج."""
        UserAchievement.objects.create(user=user, achievement_id=ach_details['id'])
        newly_unlocked.append(ach_details)
        unlocked_ids.add(ach_details['id']) # تحديث القائمة فوراً

    # --- 1. التحقق من إنجازات المراحل (Milestones) ---
    total_entries = JournalEntry.objects.filter(user=user).count()
    for key, ach in achievements['milestones'].items():
        if ach['id'] not in unlocked_ids:
            if ach['id'] == "FIRST_ENTRY_UNLOCKED" and total_entries >= 1:
                award_achievement(ach)
            elif ach['id'] == "50_ENTRIES_UNLOCKED" and total_entries >= 50:
                award_achievement(ach)
            elif ach['id'] == "100_ENTRIES_UNLOCKED" and total_entries >= 100:
                award_achievement(ach)
            elif ach['id'] == "365_ENTRIES_UNLOCKED" and total_entries >= 365:
                award_achievement(ach)

    # --- 2. التحقق من إنجازات السلاسل (Streaks) ---
    current_streak = get_user_streak(user)
    for key, ach in achievements['streaks'].items():
        if ach['id'] not in unlocked_ids:
            if current_streak >= ach['required_days']:
                award_achievement(ach)
    
    # --- 3. التحقق من إنجازات خاصة (Special) ---
    for key, ach in achievements['special'].items():
        if ach['id'] not in unlocked_ids:
            # تحقق من إنجاز "محارب نهاية الأسبوع"
            if ach['id'] == "WEEKEND_WARRIOR_UNLOCKED" and entry_time.weekday() in [4, 5]: # الجمعة=4, السبت=5
                award_achievement(ach)
            # تحقق من إنجاز "كاتب منتصف الليل"
            elif ach['id'] == "MIDNIGHT_WRITER_UNLOCKED" and 0 <= entry_time.hour < 4: # بين منتصف الليل و 4 صباحًا
                award_achievement(ach)
            # (يمكن إضافة منطق إنجاز "طيف المشاعر" هنا بتحليل محتوى اليوميات)

    return newly_unlocked