from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import JournalEntry, UserAchievement, Achievement
from users.models import CustomUser
import json
import os
from django.conf import settings
from datetime import date, timedelta
from .forms import JournalEntryForm

# تعريف بيانات الإنجازات الأساسية
ACHIEVEMENTS_DATA = {
    "streaks": {
        "FIRST_ENTRY_UNLOCKED": {
            "title": {"ar": "المبتدئ", "en": "Beginner"},
            "message": {"ar": "أكملت أول إدخال في يومياتك!", "en": "Completed your first journal entry!"},
            "badge_icon": {"ar": "<i class=\"fas fa-feather-alt\"></i>", "en": "<i class=\"fas fa-feather-alt\"></i>"},
            "required_days": 1,
            "confetti_type": "basic",
            "sound": "ding"
        },
        "SEVEN_DAYS_STREAK": {
            "title": {"ar": "المثابر", "en": "Persistent"},
            "message": {"ar": "كتبت في يومياتك لمدة 7 أيام متتالية!", "en": "Journaled for 7 consecutive days!"},
            "badge_icon": {"ar": "<i class=\"fas fa-calendar-check\"></i>", "en": "<i class=\"fas fa-calendar-check\"></i>"},
            "required_days": 7,
            "confetti_type": "stars",
            "sound": "chime"
        },
        "THIRTY_DAYS_STREAK": {
            "title": {"ar": "المنتظم", "en": "Consistent"},
            "message": {"ar": "كتبت في يومياتك لمدة 30 يومًا متتاليًا!", "en": "Journaled for 30 consecutive days!"},
            "badge_icon": {"ar": "<i class=\"fas fa-trophy\"></i>", "en": "<i class=\"fas fa-trophy\"></i>"},
            "required_days": 30,
            "confetti_type": "fountain",
            "sound": "fanfare"
        },
        "NINETY_DAYS_STREAK": {
            "title": {"ar": "المحترف", "en": "Master"},
            "message": {"ar": "كتبت في يومياتك لمدة 90 يومًا متتاليًا! إنجاز رائع!", "en": "Journaled for 90 consecutive days! Amazing achievement!"},
            "badge_icon": {"ar": "<i class=\"fas fa-star-of-life\"></i>", "en": "<i class=\"fas fa-star-of-life\"></i>"},
            "required_days": 90,
            "confetti_type": "fireworks",
            "sound": "success_bell"
        }
    },
    "milestones": {
        "FIRST_GOAL_COMPLETED": {
            "title": {"ar": "مُحقق الأهداف", "en": "Goal Achiever"},
            "message": {"ar": "أكملت أول هدف لك بنجاح!", "en": "Successfully completed your first goal!"},
            "badge_icon": {"ar": "<i class=\"fas fa-bullseye\"></i>", "en": "<i class=\"fas fa-bullseye\"></i>"},
            "confetti_type": "basic",
            "sound": "ding"
        },
        "FIVE_GOALS_COMPLETED": {
            "title": {"ar": "سيد الأهداف", "en": "Goal Master"},
            "message": {"ar": "أكملت 5 أهداف! أنت تتحرك نحو الأفضل.", "en": "Completed 5 goals! You're moving forward."},
            "badge_icon": {"ar": "<i class=\"fas fa-medal\"></i>", "en": "<i class=\"fas fa-medal\"></i>"},
            "confetti_type": "stars",
            "sound": "chime"
        }
    },
    "special": {
        "FIRST_COMPANION_CHAT": {
            "title": {"ar": "رفيق الدرب", "en": "Companion Initiator"},
            "message": {"ar": "تحدثت مع رفيق الدرب لأول مرة!", "en": "Chatted with the Companion for the first time!"},
            "badge_icon": {"ar": "<i class=\"fas fa-robot\"></i>", "en": "<i class=\"fas fa-robot\"></i>"},
            "confetti_type": "basic",
            "sound": "ding"
        }
    }
}

def calculate_streak(user):
    """حساب السلسلة (streak) للمستخدم."""
    today = timezone.localdate()  # 08:58 PM +03, 22 يوليو 2025
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
                    break
            if streak > 365 * 10:  # حد أقصى لمنع الحلقات الطويلة
                break
    return streak

@login_required
def dashboard_view(request):
    """
    Displays the user's dashboard, including journal entry form and streak.
    Handles achievement checking and unlocking.
    """
    today = timezone.localdate()  # 08:58 PM +03, 22 يوليو 2025
    entry, created = JournalEntry.objects.get_or_create(user=request.user, entry_date=today)

    # تعيين start_date إذا لم يكن معينًا
    if not request.user.start_date:
        request.user.start_date = today
        request.user.save()
        print(f"Set start_date for {request.user.username} to {today}")

    # حساب السلسلة باستخدام الدالة المستقلة
    streak = calculate_streak(request.user)

    if request.method == 'POST':
        daily_entry_content = request.POST.get('daily_entry')
        if daily_entry_content:
            entry.content = daily_entry_content
            entry.save()
            messages.success(request, "تم حفظ يومياتك بنجاح!")
            check_and_unlock_achievements(request.user)
            return redirect('dashboard')
        else:
            messages.error(request, "لا يمكن حفظ يومية فارغة.")

    # فتح الإنجازات الجديدة للنافذة المنبثقة
    unlocked_achievements_for_popup = []
    for ach_category in ["streaks", "milestones", "special"]:
        for ach_id, ach_data in ACHIEVEMENTS_DATA.get(ach_category, {}).items():
            if ach_category == "streaks" and ach_data.get("required_days") and streak >= ach_data["required_days"]:
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
            elif ach_category == "milestones" and ach_id == "FIRST_GOAL_COMPLETED" and not UserAchievement.objects.filter(user=request.user, achievement_id=ach_id).exists():
                # منطق افتراضي لـ FIRST_GOAL_COMPLETED (يتطلب تحققًا إضافيًا)
                UserAchievement.objects.create(user=request.user, achievement_id=ach_id)
                unlocked_achievements_for_popup.append({
                    "id": ach_id,
                    "title": ach_data["title"],
                    "description": ach_data["message"],
                    "icon": ach_data["badge_icon"],
                    "confetti_type": ach_data.get("confetti_type", "basic"),
                    "sound": ach_data.get("sound", "ding")
                })

    # إعداد بيانات JavaScript (بدون اقتباسات)
    all_achievements_js_data = {
        "achievements": ACHIEVEMENTS_DATA,
        "confetti_types": {
            "basic": {"particleCount": 100, "spread": 70},
            "stars": {"particleCount": 150, "spread": 90, "shapes": ["star"], "colors": ["#FFD700", "#FFA500"]},
            "fountain": {"particleCount": 200, "spread": 120, "startVelocity": 30, "scalar": 1.2},
            "fireworks": {"particleCount": 250, "spread": 180, "startVelocity": 45, "scalar": 1.5, "gravity": 0.5, "decay": 0.9},
        },
        "sounds": {
            "ding": "/static/sounds/ding.mp3",
            "chime": "/static/sounds/chime.mp3",
            "fanfare": "/static/sounds/fanfare.mp3",
            "success_bell": "/static/sounds/success_bell.mp3",
        },
        "newly_unlocked_for_popup": unlocked_achievements_for_popup,
    }

    # حساب أيام التقدم
    days_passed = 0
    target_days = 90
    if request.user.start_date:
        days_passed = (today - request.user.start_date).days + 1
        if days_passed < 0:
            days_passed = 0
    print(f"Days passed: {days_passed}, Target days: {target_days} for user {request.user.username}")

    # مستوى الشخصية
    character_level = min(streak // 10, 5)

    # السياق (بدون اقتباسات)
    context = {
        'entry': entry,
        'already_written_today': entry.content is not None and entry.content.strip() != '',
        'streak': streak,
        'days_passed': days_passed,
        'target_days': target_days,
        'character_level': character_level,
        'all_achievements_data_json': json.dumps(all_achievements_js_data, ensure_ascii=False),
    }

    return render(request, 'journal/dashboard.html', context)

def check_and_unlock_achievements(user):
    """A separate function to check and unlock achievements."""
    streak = calculate_streak(user)

    for ach_category in ["streaks", "milestones", "special"]:
        for ach_id, ach_data in ACHIEVEMENTS_DATA.get(ach_category, {}).items():
            if ach_category == "streaks" and ach_data.get("required_days") and streak >= ach_data["required_days"]:
                if not UserAchievement.objects.filter(user=user, achievement_id=ach_id).exists():
                    UserAchievement.objects.create(user=user, achievement_id=ach_id)
                    messages.info(user, f"تم فتح إنجاز جديد: {ach_data['title']['ar']}!")
            elif ach_category == "milestones" and ach_id == "FIRST_GOAL_COMPLETED" and not UserAchievement.objects.filter(user=user, achievement_id=ach_id).exists():
                # منطق افتراضي لـ FIRST_GOAL_COMPLETED (يتطلب تحققًا إضافيًا)
                UserAchievement.objects.create(user=user, achievement_id=ach_id)
                messages.info(user, f"تم فتح إنجاز جديد: {ach_data['title']['ar']}!")

@login_required
def journal_entries_view(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-entry_date')
    return render(request, 'journal/my_journal.html', {'entries': entries})

@login_required
def goals_view(request):
    return render(request, 'journal/goals.html')

@login_required
def companion_view(request):
    return render(request, 'journal/companion.html')

@login_required
def add_entry_view(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.entry_date = timezone.localdate()
            entry.save()
            messages.success(request, 'تم حفظ اليومية بنجاح!')
            check_and_unlock_achievements(request.user)
            return redirect('dashboard')
    else:
        form = JournalEntryForm()
    return render(request, 'journal/add_entry.html', {'form': form})

@login_required
def edit_entry_view(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل اليومية بنجاح!')
            return redirect('journal:journal_entries')
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'journal/edit_entry.html', {'form': form})

@login_required
def delete_entry_view(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'تم حذف اليومية بنجاح!')
        return redirect('journal:journal_entries')
    return render(request, 'journal/delete_entry.html', {'entry': entry})

@login_required
def achievements_view(request):
    # جلب بيانات الإنجازات من النموذج Achievement
    achievements = Achievement.objects.filter(user=request.user)
    achievements_data = {
        'achievements': {
            'streaks': {},
            'milestones': {},
            'special': {},
        },
    }

    for ach in achievements:
        ach_data = {
            'title': ach.title,
            'message': ach.description,
            'badge_icon': ach.icon,
            'unlocked': ach.unlocked,
            'unlocked_at': ach.unlocked_at,
            'required_days': ach.required_days if hasattr(ach, 'required_days') else None,
        }
        if ach.type == 'streak':
            achievements_data['achievements']['streaks'][ach.id] = ach_data
        elif ach.type == 'milestone':
            achievements_data['achievements']['milestones'][ach.id] = ach_data
        elif ach.type == 'special':
            achievements_data['achievements']['special'][ach.id] = ach_data

    context = {
        'all_achievements_data_json': json.dumps(achievements_data, ensure_ascii=False),
    }
    return render(request, 'journal/achievements.html', context)