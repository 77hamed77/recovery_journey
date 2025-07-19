# journal/achievements_engine.py

import json
from pathlib import Path
from datetime import date, timedelta, datetime
from django.conf import settings
from django.contrib.auth.models import User
from .models import JournalEntry, UserAchievement
from users.models import Profile # استيراد نموذج الملف الشخصي

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
    entry_dates = list(user.journalentry_set.order_by('-entry_date').values_list('entry_date', flat=True).distinct())
    if not entry_dates:
        return 0
    streak = 0
    today = date.today()
    if entry_dates[0] == today or entry_dates[0] == today - timedelta(days=1):
        streak = 1
        for i in range(len(entry_dates) - 1):
            if entry_dates[i] - entry_dates[i+1] == timedelta(days=1):
                streak += 1
            else:
                break
    return streak

def check_and_award_achievements(user: User, entry_time: datetime, entry_content: str = "") -> list:
    """
    الوظيفة الرئيسية والمحسّنة للتحقق من الإنجازات.
    """
    all_achievements_data = get_achievements_data()
    achievements = all_achievements_data['achievements']
    settings_data = all_achievements_data.get('settings', {})
    
    # 1. تحديد تفضيل المستخدم
    try:
        user_pref = user.profile.content_preference
    except Profile.DoesNotExist:
        user_pref = 'muslim'  # قيمة افتراضية آمنة

    # 2. الكشف التلقائي عن المحتوى (إذا كان مفعّلاً في JSON)
    if settings_data.get('auto_detect_content', False):
        if any(keyword in entry_content.lower() for keyword in settings_data['detection_keywords']['muslim']):
            user_pref = 'muslim'
    
    unlocked_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))
    newly_unlocked = []

    def get_localized_achievement(ach_details, pref):
        """دالة مساعدة لمعالجة النصوص والأيقونات متعددة اللغات."""
        processed_ach = ach_details.copy()
        if isinstance(ach_details.get('title'), dict):
            processed_ach['title'] = ach_details['title'].get(pref, ach_details['title']['universal'])
        if isinstance(ach_details.get('message'), dict):
            processed_ach['message'] = ach_details['message'].get(pref, ach_details['message']['universal'])
        if isinstance(ach_details.get('badge_icon'), dict):
            processed_ach['badge_icon'] = ach_details['badge_icon'].get(pref, ach_details['badge_icon']['universal'])
        return processed_ach

    def award_achievement(ach_details, pref):
        """دالة مساعدة لتسجيل إنجاز جديد."""
        localized_ach = get_localized_achievement(ach_details, pref)
        if localized_ach['id'] not in unlocked_ids:
            UserAchievement.objects.create(user=user, achievement_id=localized_ach['id'])
            newly_unlocked.append(localized_ach)
            unlocked_ids.add(localized_ach['id'])

    # 3. التحقق من الإنجازات
    
    # التحقق من إنجازات المراحل (Milestones)
    total_entries = JournalEntry.objects.filter(user=user).count()
    for key, ach in achievements['milestones'].items():
        if (ach['id'] == "FIRST_ENTRY_UNLOCKED" and total_entries >= 1) or \
           (ach['id'] == "40_ENTRIES_UNLOCKED" and total_entries >= 40) or \
           (ach['id'] == "100_ENTRIES_UNLOCKED" and total_entries >= 100) or \
           (ach['id'] == "365_ENTRIES_UNLOCKED" and total_entries >= 365):
            award_achievement(ach, user_pref)

    # التحقق من إنجازات السلاسل (Streaks)
    current_streak = get_user_streak(user)
    for key, ach in achievements['streaks'].items():
        if current_streak >= ach['required_days']:
            award_achievement(ach, user_pref)
    
    # التحقق من إنجازات خاصة (Special)
    for key, ach in achievements['special'].items():
        # تحقق من إنجاز نهاية الأسبوع
        if ach['id'] == "WEEKEND_COMMITMENT_UNLOCKED" and entry_time.weekday() in [4, 5]:  # الجمعة=4, السبت=5
            award_achievement(ach, user_pref)
        # تحقق من إنجاز الفجر
        elif ach['id'] == "EARLY_REFLECTION_UNLOCKED" and 3 <= entry_time.hour < 6: # بين 3 و 6 صباحًا
            award_achievement(ach, user_pref)
        # تحقق من إنجاز الشكر والامتنان
        elif ach['id'] == "GRATITUDE_MASTER_UNLOCKED":
             gratitude_keywords = ["الحمد لله", "شكراً يا رب", "ممتن", "أشكرك"]
             if any(keyword in entry_content for keyword in gratitude_keywords):
                award_achievement(ach, user_pref)

    return newly_unlocked