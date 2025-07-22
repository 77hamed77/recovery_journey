# journal/achievements_engine.py

import json
from pathlib import Path
from datetime import date, timedelta, datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import F # لاستخدام F expressions لتحسين الاستعلامات
from .models import JournalEntry, UserAchievement
# تأكد من أن نموذج Profile موجود في 'users.models' أو قم بتعديل المسار حسب مشروعك
try:
    from users.models import Profile
except ImportError:
    # توفير حل بديل أو تسجيل خطأ إذا لم يتم العثور على Profile
    class Profile:
        content_preference = 'universal' # قيمة افتراضية إذا لم يكن هناك نموذج Profile
        def __init__(self, *args, **kwargs):
            pass
    print("تحذير: لم يتم العثور على نموذج Profile في users.models. سيتم استخدام تفضيل محتوى افتراضي.")


# تحديد مسار ملف الإنجازات بشكل آمن باستخدام Path
ACHIEVEMENTS_FILE = Path(settings.BASE_DIR) / "static/data/achievements.json"

def get_achievements_data() -> dict:
    """
    يقرأ ويعيد بيانات الإنجازات من ملف JSON.
    يتعامل مع الأخطاء المحتملة أثناء قراءة الملف.
    """
    try:
        with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"خطأ: ملف الإنجازات غير موجود في المسار: {ACHIEVEMENTS_FILE}")
        return {"achievements": {}, "settings": {}} # إرجاع بنية فارغة لتجنب الأخطاء
    except json.JSONDecodeError:
        print(f"خطأ: فشل تحليل ملف JSON للإنجازات: {ACHIEVEMENTS_FILE}")
        return {"achievements": {}, "settings": {}}

def get_user_streak(user: User) -> int:
    """
    دالة محسّنة لحساب عدد الأيام المتتالية التي كتب فيها المستخدم.
    تعتبر السلسلة مستمرة إذا كانت اليومية مكتوبة اليوم أو أمس.
    """
    # جلب جميع تواريخ اليوميات للمستخدم، مرتبة تنازليًا، وفريدة.
    # استخدام `values_list` و `flat=True` يجلب قائمة بالتواريخ فقط.
    entry_dates = list(user.journal_entries.order_by('-entry_date').values_list('entry_date', flat=True).distinct())

    if not entry_dates:
        return 0 # لا توجد يوميات، لا توجد سلسلة

    streak = 0
    today = date.today() # التاريخ الحالي بدون وقت

    # التحقق مما إذا كانت أحدث يومية هي اليوم أو أمس لبدء السلسلة
    # هذا يسمح باستمرارية السلسلة حتى لو لم يكتب المستخدم اليوم بعد
    if entry_dates[0] == today:
        current_date_check = today
    elif entry_dates[0] == today - timedelta(days=1):
        current_date_check = today - timedelta(days=1)
    else:
        return 0 # أحدث يومية ليست اليوم أو أمس، السلسلة مكسورة

    # حساب السلسلة
    for entry_date in entry_dates:
        if entry_date == current_date_check:
            streak += 1
            current_date_check -= timedelta(days=1) # الانتقال إلى اليوم السابق في السلسلة
        elif entry_date < current_date_check:
            # إذا كان التاريخ أقدم من المتوقع، فهذا يعني وجود فجوة في السلسلة
            break
        # إذا كان التاريخ أحدث من current_date_check (وهو ما لا يجب أن يحدث بسبب الترتيب)، استمر
    return streak


def check_and_award_achievements(user: User, entry_time: datetime, entry_content: str = "") -> list:
    """
    الوظيفة الرئيسية والمحسّنة للتحقق من الإنجازات ومنحها للمستخدم.
    تأخذ في الاعتبار تفضيلات المستخدم ومحتوى اليومية.
    """
    all_achievements_data = get_achievements_data()
    achievements_config = all_achievements_data.get('achievements', {})
    settings_data = all_achievements_data.get('settings', {})

    # 1. تحديد تفضيل المستخدم
    user_pref = 'universal' # قيمة افتراضية
    try:
        # محاولة جلب تفضيل المحتوى من ملف تعريف المستخدم
        user_pref = user.profile.content_preference
    except Profile.DoesNotExist:
        pass # إذا لم يكن هناك ملف تعريف، استخدم القيمة الافتراضية

    # 2. الكشف التلقائي عن المحتوى (إذا كان مفعّلاً في JSON)
    # هذا يسمح بتجاوز تفضيل المستخدم بناءً على محتوى اليومية
    if settings_data.get('auto_detect_content', False):
        detection_keywords = settings_data.get('detection_keywords', {})
        # التحقق من الكلمات الدلالية للمحتوى الإسلامي (مثال)
        if any(keyword in entry_content.lower() for keyword in detection_keywords.get('muslim', [])):
            user_pref = 'muslim'
        # يمكن إضافة المزيد من الفئات هنا (مثال: 'christian', 'general_wellness')

    # جلب معرفات الإنجازات المفتوحة حاليًا للمستخدم لتحسين الأداء
    unlocked_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))
    newly_unlocked = [] # قائمة لتخزين الإنجازات الجديدة التي تم فتحها

    def get_localized_achievement(ach_details: dict, pref: str) -> dict:
        """
        دالة مساعدة لمعالجة النصوص والأيقونات متعددة اللغات للإنجاز.
        تفضل النص الخاص بالتفضيل المحدد، ثم النص العام (universal).
        """
        processed_ach = ach_details.copy()
        # معالجة العنوان
        if isinstance(ach_details.get('title'), dict):
            processed_ach['title'] = ach_details['title'].get(pref, ach_details['title'].get('universal', ''))
        # معالجة الرسالة
        if isinstance(ach_details.get('message'), dict):
            processed_ach['message'] = ach_details['message'].get(pref, ach_details['message'].get('universal', ''))
        # معالجة أيقونة الشارة
        if isinstance(ach_details.get('badge_icon'), dict):
            processed_ach['badge_icon'] = ach_details['badge_icon'].get(pref, ach_details['badge_icon'].get('universal', ''))
        return processed_ach

    def award_achievement(ach_details: dict, pref: str):
        """
        دالة مساعدة لتسجيل إنجاز جديد للمستخدم إذا لم يكن قد تم فتحه بالفعل.
        """
        localized_ach = get_localized_achievement(ach_details, pref)
        if localized_ach['id'] not in unlocked_ids:
            # إنشاء إدخال جديد في نموذج UserAchievement
            UserAchievement.objects.create(user=user, achievement_id=localized_ach['id'])
            newly_unlocked.append(localized_ach) # إضافة الإنجاز الجديد إلى قائمة المفتوحة حديثًا
            unlocked_ids.add(localized_ach['id']) # تحديث مجموعة الإنجازات المفتوحة

    # 3. التحقق من الإنجازات بناءً على أنواعها
    
    # التحقق من إنجازات المراحل (Milestones)
    # استخدام `count()` مباشرة على الاستعلام لتحسين الأداء
    total_entries = user.journal_entries.count()
    for key, ach in achievements_config.get('milestones', {}).items():
        required_entries = ach.get('required_entries')
        if required_entries is not None and total_entries >= required_entries:
            award_achievement(ach, user_pref)

    # التحقق من إنجازات السلاسل (Streaks)
    current_streak = get_user_streak(user)
    for key, ach in achievements_config.get('streaks', {}).items():
        required_days = ach.get('required_days')
        if required_days is not None and current_streak >= required_days:
            award_achievement(ach, user_pref)
    
    # التحقق من إنجازات خاصة (Special)
    for key, ach in achievements_config.get('special', {}).items():
        ach_id = ach.get('id')
        if ach_id == "WEEKEND_COMMITMENT_UNLOCKED":
            # التحقق من إنجاز نهاية الأسبوع (الجمعة والسبت في معظم الثقافات العربية)
            # الجمعة = 4, السبت = 5 في Python's weekday()
            if entry_time.weekday() in [4, 5]:
                award_achievement(ach, user_pref)
        elif ach_id == "EARLY_REFLECTION_UNLOCKED":
            # التحقق من إنجاز الفجر (بين 3 و 6 صباحًا)
            if 3 <= entry_time.hour < 6:
                award_achievement(ach, user_pref)
        elif ach_id == "GRATITUDE_MASTER_UNLOCKED":
            # التحقق من إنجاز الشكر والامتنان
            gratitude_keywords = ach.get('keywords', []) # جلب الكلمات المفتاحية من JSON
            if any(keyword in entry_content for keyword in gratitude_keywords):
                award_achievement(ach, user_pref)
        # يمكن إضافة المزيد من الشروط للإنجازات الخاصة هنا

    return newly_unlocked
