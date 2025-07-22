# journal/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import JournalEntry, UserAchievement
from users.models import CustomUser # لاستيراد CustomUser إذا لزم الأمر في الـ dashboard_view
import json 
from datetime import date, timedelta
from .forms import JournalEntryForm # تأكد من استيراد JournalEntryForm
import os # لاستخدام os.path
from django.conf import settings # لاستخدام settings.STATICFILES_DIRS

# تعريف بيانات الإنجازات مع دعم التدويل والتصنيف (كما هو في التعديل السابق)
# هذه البيانات هي تعريفات الإنجازات نفسها، وليس الاقتباسات
ACHIEVEMENTS_DATA = {
    "streaks": {
        "FIRST_ENTRY_UNLOCKED": {
            "title": {"ar": "المبتدئ", "en": "Beginner"},
            "message": {"ar": "أكملت أول إدخال في يومياتك!", "en": "Completed your first journal entry!"},
            "badge_icon": {"ar": '<i class="fas fa-feather-alt"></i>', "en": '<i class="fas fa-feather-alt"></i>'},
            "required_days": 1,
            "confetti_type": "basic",
            "sound": "ding"
        },
        "SEVEN_DAYS_STREAK": {
            "title": {"ar": "المثابر", "en": "Persistent"},
            "message": {"ar": "كتبت في يومياتك لمدة 7 أيام متتالية!", "en": "Journaled for 7 consecutive days!"},
            "badge_icon": {"ar": '<i class="fas fa-calendar-check"></i>', "en": '<i class="fas fa-calendar-check"></i>'},
            "required_days": 7,
            "confetti_type": "stars",
            "sound": "chime"
        },
        "THIRTY_DAYS_STREAK": {
            "title": {"ar": "المنتظم", "en": "Consistent"},
            "message": {"ar": "كتبت في يومياتك لمدة 30 يومًا متتاليًا!", "en": "Journaled for 30 consecutive days!"},
            "badge_icon": {"ar": '<i class="fas fa-trophy"></i>', "en": '<i class="fas fa-trophy"></i>'},
            "required_days": 30,
            "confetti_type": "fountain",
            "sound": "fanfare"
        },
        "NINETY_DAYS_STREAK": {
            "title": {"ar": "المحترف", "en": "Master"},
            "message": {"ar": "كتبت في يومياتك لمدة 90 يومًا متتاليًا! إنجاز رائع!", "en": "Journaled for 90 consecutive days! Amazing achievement!"},
            "badge_icon": {"ar": '<i class="fas fa-star-of-life"></i>', "en": '<i class="fas fa-star-of-life"></i>'},
            "required_days": 90,
            "confetti_type": "fireworks",
            "sound": "success_bell"
        },
    },
    "milestones": {
        "FIRST_GOAL_COMPLETED": {
            "title": {"ar": "مُحقق الأهداف", "en": "Goal Achiever"},
            "message": {"ar": "أكملت أول هدف لك بنجاح!", "en": "Successfully completed your first goal!"},
            "badge_icon": {"ar": '<i class="fas fa-bullseye"></i>', "en": '<i class="fas fa-bullseye"></i>'},
            "confetti_type": "basic",
            "sound": "ding"
        },
        "FIVE_GOALS_COMPLETED": {
            "title": {"ar": "سيد الأهداف", "en": "Goal Master"},
            "message": {"ar": "أكملت 5 أهداف! أنت تتحرك نحو الأفضل.", "en": "Completed 5 goals! You're moving forward."},
            "badge_icon": {"ar": '<i class="fas fa-medal"></i>', "en": '<i class="fas fa-medal"></i>'},
            "confetti_type": "stars",
            "sound": "chime"
        },
    },
    "special": {
        "FIRST_COMPANION_CHAT": {
            "title": {"ar": "رفيق الدرب", "en": "Companion Initiator"},
            "message": {"ar": "تحدثت مع رفيق الدرب لأول مرة!", "en": "Chatted with the Companion for the first time!"},
            "badge_icon": {"ar": '<i class="fas fa-robot"></i>', "en": '<i class="fas fa-robot"></i>'},
            "confetti_type": "basic",
            "sound": "ding"
        },
        # أضف المزيد من الإنجازات الخاصة هنا
    }
}


# ===================================================================
# Journal Entry Views
# ===================================================================

@login_required
def dashboard_view(request):
    """
    Displays the user's dashboard, including journal entry form and streak.
    Handles achievement checking and unlocking.
    """
    today = timezone.localdate()
    # Attempt to get today's entry, or create a new one
    entry, created = JournalEntry.objects.get_or_create(user=request.user, entry_date=today)

    # Calculate streak
    streak = 0
    if request.user.start_date: # Assuming CustomUser has a start_date field
        current_date = today
        while True:
            # Check if there's an entry for the current date
            if JournalEntry.objects.filter(user=request.user, entry_date=current_date).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                # If there's a gap, check if the previous day was the start date
                if current_date == request.user.start_date - timedelta(days=1):
                    # If the streak goes back to the day before the start date, it's valid
                    break
                elif current_date < request.user.start_date:
                    # If we went before the start date without finding entries, stop
                    break
                else:
                    # Gap found, streak broken
                    streak = 0
                    break
            
            # Prevent infinite loop if something goes wrong
            if streak > 365 * 10: # Max 10 years streak
                break

    # Handle form submission for journal entry
    if request.method == 'POST':
        daily_entry_content = request.POST.get('daily_entry')
        if daily_entry_content:
            entry.content = daily_entry_content
            entry.save()
            messages.success(request, "تم حفظ يومياتك بنجاح!")
            # Trigger achievement check after saving the entry
            # This part should be handled by a signal or a dedicated function
            # For simplicity, we'll call it directly here for now.
            check_and_unlock_achievements(request.user)
            return redirect('dashboard') # Redirect to refresh the page and show success/updated content
        else:
            messages.error(request, "لا يمكن حفظ يومية فارغة.")

    # Check for achievements based on the new structure
    unlocked_achievements_for_popup = []
    
    # Streak Achievements
    for ach_id, ach_data in ACHIEVEMENTS_DATA["streaks"].items():
        if ach_data.get("required_days") and streak >= ach_data["required_days"]:
            if not UserAchievement.objects.filter(user=request.user, achievement_id=ach_id).exists():
                UserAchievement.objects.create(user=request.user, achievement_id=ach_id)
                unlocked_achievements_for_popup.append({
                    "id": ach_id,
                    "title": ach_data["title"],
                    "description": ach_data["message"],
                    "icon": ach_data["badge_icon"],
                    "confetti_type": ach_data.get("confetti_type", "basic"),
                    "sound": ach_data.get("sound", "ding")
                })
    
    # --- Load Quotes from achievements.json ---
    quotes_data = {}
    # هذا هو المسار الذي يجب أن يكون صحيحًا بناءً على هيكلية مشروعك
    # إذا كان achievements.json في مجلد static/json داخل تطبيق journal
    json_file_path = os.path.join(settings.BASE_DIR, 'journal', 'static', 'json', 'achievements.json')
    
    print(f"Attempting to load quotes from: {json_file_path}") # لغرض التشخيص

    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                quotes_data = json.load(f)
            print("Quotes loaded successfully. Content structure sample:")
            # اطبع جزءًا من البيانات للتحقق من التنسيق
            print(json.dumps(quotes_data.get("quotes", {}).get("universal", [])[:1], indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_file_path}: {e}")
            quotes_data = {"quotes": {"universal": [{"text": "خطأ في تحميل الاقتباسات (تنسيق JSON غير صالح).", "author": "النظام"}]}}
        except Exception as e:
            print(f"An unexpected error occurred while loading {json_file_path}: {e}")
            quotes_data = {"quotes": {"universal": [{"text": "خطأ غير متوقع في تحميل الاقتباسات.", "author": "النظام"}]}}
    else:
        print(f"achievements.json not found at {json_file_path}")
        quotes_data = {"quotes": {"universal": [{"text": "ملف الاقتباسات غير موجود في المسار المحدد.", "author": "النظام"}]}}

    # Pass achievement data and quotes to template for JavaScript popups
    all_achievements_js_data = {
        "achievements": ACHIEVEMENTS_DATA, # Pass the full definition for reference
        "confetti_types": {
            "basic": {"particleCount": 100, "spread": 70},
            "stars": {"particleCount": 150, "spread": 90, "shapes": ['star'], "colors": ['#FFD700', '#FFA500']},
            "fountain": {"particleCount": 200, "spread": 120, "startVelocity": 30, "scalar": 1.2},
            "fireworks": {"particleCount": 250, "spread": 180, "startVelocity": 45, "scalar": 1.5, "gravity": 0.5, "decay": 0.9},
        },
        "sounds": {
            "ding": "/static/sounds/ding.mp3", # استخدام المسار المطلق
            "chime": "/static/sounds/chime.mp3",
            "fanfare": "/static/sounds/fanfare.mp3",
            "success_bell": "/static/sounds/success_bell.mp3",
        },
        "newly_unlocked_for_popup": unlocked_achievements_for_popup, # Achievements to show popup for
        "quotes": quotes_data.get("quotes", {"universal": [{"text": "لا توجد اقتباسات متاحة حاليًا.", "author": "النظام"}]}) # إضافة الاقتباسات هنا
    }

    # Calculate days passed for the 90-day journey progress bar
    days_passed = 0
    target_days = 90 # You can make this configurable
    if request.user.start_date:
        days_passed = (today - request.user.start_date).days + 1
        if days_passed < 0: days_passed = 0 # Ensure it's not negative

    # Determine character level based on streak or other metrics
    # This is a simple example; you might have more complex logic
    character_level = min(streak // 10, 5) # Example: level up every 10 days, max level 5

    context = {
        'entry': entry,
        'already_written_today': entry.content is not None and entry.content.strip() != '', # Check if content exists
        'streak': streak,
        'days_passed': days_passed,
        'target_days': target_days,
        'character_level': character_level,
        'all_achievements_data_json': json.dumps(all_achievements_js_data, ensure_ascii=False), # لـ JavaScript
    }
    print("Context passed to template (all_achievements_data_json):")
    print(json.dumps(all_achievements_js_data.get("quotes", {}).get("universal", [])[:1], indent=2, ensure_ascii=False))

    return render(request, 'journal/dashboard.html', context)


def check_and_unlock_achievements(user):
    """
    A separate function to check and unlock achievements.
    This can be called from different views or signals.
    """
    today = timezone.localdate()
    # Recalculate streak
    streak = 0
    if user.start_date:
        current_date = today
        while True:
            if JournalEntry.objects.filter(user=user, entry_date=current_date).exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                if current_date == user.start_date - timedelta(days=1):
                    break
                elif current_date < user.start_date:
                    break
                else:
                    streak = 0
                    break
            if streak > 365 * 10:
                break

    for ach_id, ach_data in ACHIEVEMENTS_DATA["streaks"].items():
        if ach_data.get("required_days") and streak >= ach_data["required_days"]:
            if not UserAchievement.objects.filter(user=user, achievement_id=ach_id).exists():
                UserAchievement.objects.create(user=user, achievement_id=ach_id)
                # You might want to add a message or trigger a popup here
                # For now, we'll assume the dashboard view will handle popups on load
                messages.info(user, f"تم فتح إنجاز جديد: {ach_data['title']['ar']}!")

    # Example for milestone achievement (e.g., first goal completed)
    # You would need to import Goal model and check if goals are completed
    # from goals.models import Goal
    # if Goal.objects.filter(user=user, completed=True).exists():
    #     if not UserAchievement.objects.filter(user=user, achievement_id="FIRST_GOAL_COMPLETED").exists():
    #         UserAchievement.objects.create(user=user, achievement_id="FIRST_GOAL_COMPLETED")
    #         messages.info(user, "تم فتح إنجاز: محقق الأهداف!")


# ===================================================================
# Achievements View
# ===================================================================

@login_required
def achievements_view(request):
    """
    Displays all achievements for the current user, categorized and localized.
    """
    user_unlocked_achievements = UserAchievement.objects.filter(user=request.user)
    unlocked_ids = {ach.achievement_id for ach in user_unlocked_achievements}
    unlocked_map = {ach.achievement_id: ach.unlocked_at for ach in user_unlocked_achievements}

    # Prepare a nested dictionary that mirrors ACHIEVEMENTS_DATA structure
    # but also includes 'unlocked' status and 'unlocked_at' timestamp
    categorized_achievements_for_template = {
        "streaks": {},
        "milestones": {},
        "special": {}
    }

    for category, achievements_dict in ACHIEVEMENTS_DATA.items():
        for ach_id, ach_data in achievements_dict.items():
            is_unlocked = ach_id in unlocked_ids
            
            categorized_achievements_for_template[category][ach_id] = {
                **ach_data, # Copy all definition data (title, message, icon, etc.)
                'unlocked': is_unlocked,
                'unlocked_at': unlocked_map.get(ach_id) if is_unlocked else None,
            }
    
    context = {
        'all_achievements_data_json': { # Renamed to match template's expected variable
            'achievements': categorized_achievements_for_template
        },
    }
    return render(request, 'journal/achievements.html', context)

# ===================================================================
# My Journals View (عرض جميع اليوميات)
# ===================================================================

@login_required
def my_journals_view(request):
    """
    Displays a list of all journal entries for the current user.
    """
    # جلب جميع اليوميات للمستخدم الحالي، مرتبة تنازلياً حسب التاريخ
    entries = JournalEntry.objects.filter(user=request.user).order_by('-entry_date')
    context = {
        'entries': entries,
    }
    return render(request, 'journal/my_journals.html', context)

# ===================================================================
# Edit Journal Entry View (تعديل يومية)
# ===================================================================

@login_required
def edit_journal_entry(request, entry_id):
    """
    Allows the user to edit a specific journal entry.
    """
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث اليومية بنجاح!")
            return redirect('journal:my_journals') # إعادة التوجيه إلى قائمة اليوميات
        else:
            messages.error(request, "حدث خطأ أثناء تحديث اليومية. الرجاء التحقق من البيانات.")
    else:
        form = JournalEntryForm(instance=entry)
    
    context = {
        'form': form,
        'entry': entry,
    }
    return render(request, 'journal/edit_journal_entry.html', context)

# ===================================================================
# Delete Journal Entry View (حذف يومية)
# ===================================================================

@login_required
def delete_journal_entry(request, entry_id):
    """
    Allows the user to delete a specific journal entry.
    """
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "تم حذف اليومية بنجاح!")
        return redirect('journal:my_journals')
    
    context = {
        'entry': entry,
    }
    return render(request, 'journal/confirm_delete_journal_entry.html', context) # قالب لتأكيد الحذف
