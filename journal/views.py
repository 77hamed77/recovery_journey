from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Max
from .models import JournalEntry, UserAchievement, Achievement
from users.models import CustomUser
import json
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
        "ONE_WEEK_STREAK": {
            "title": {"ar": "أسبوع نظيف", "en": "Clean Week"},
            "message": {"ar": "أكملت أسبوعًا كاملاً بدون نكسة!", "en": "Completed a full week without a relapse!"},
            "badge_icon": {"ar": "<i class=\"fas fa-calendar-check\"></i>", "en": "<i class=\"fas fa-calendar-check\"></i>"},
            "required_days": 7,
            "confetti_type": "stars",
            "sound": "chime"
        },
        "TWO_WEEKS_STREAK": {
            "title": {"ar": "أسبوعان نظيفان", "en": "Two Clean Weeks"},
            "message": {"ar": "أكملت أسبوعين كاملين بدون نكسة!", "en": "Completed two full weeks without a relapse!"},
            "badge_icon": {"ar": "<i class=\"fas fa-calendar-star\"></i>", "en": "<i class=\"fas fa-calendar-star\"></i>"},
            "required_days": 14,
            "confetti_type": "fountain",
            "sound": "fanfare"
        },
        "ONE_MONTH_STREAK": {
            "title": {"ar": "شهر نظيف", "en": "Clean Month"},
            "message": {"ar": "أكملت شهرًا كاملاً بدون نكسة!", "en": "Completed a full month without a relapse!"},
            "badge_icon": {"ar": "<i class=\"fas fa-trophy\"></i>", "en": "<i class=\"fas fa-trophy\"></i>"},
            "required_days": 30,
            "confetti_type": "fireworks",
            "sound": "success_bell"
        },
        "THREE_MONTHS_STREAK": {
            "title": {"ar": "ثلاثة أشهر نظيفة", "en": "Three Clean Months"},
            "message": {"ar": "أكملت ثلاثة أشهر كاملة بدون نكسة!", "en": "Completed three full months without a relapse!"},
            "badge_icon": {"ar": "<i class=\"fas fa-medal\"></i>", "en": "<i class=\"fas fa-medal\"></i>"},
            "required_days": 90,
            "confetti_type": "fireworks",
            "sound": "fanfare"
        }
    },
    "milestones": {
        "FIRST_GOAL_COMPLETED": {
            "title": {"ar": "الهدف الأول", "en": "First Goal"},
            "message": {"ar": "أكملت هدفك الأول في رحلة التعافي!", "en": "Completed your first goal in your recovery journey!"},
            "badge_icon": {"ar": "<i class=\"fas fa-check-circle\"></i>", "en": "<i class=\"fas fa-check-circle\"></i>"},
            "confetti_type": "basic",
            "sound": "ding"
        }
    },
    "special": {
        "PERFECT_STREAK": {
            "title": {"ar": "السلسلة المثالية", "en": "Perfect Streak"},
            "message": {"ar": "حافظت على سلسلة مثالية لمدة 90 يومًا بدون نكسة!", "en": "Maintained a perfect streak for 90 days without a relapse!"},
            "badge_icon": {"ar": "<i class=\"fas fa-crown\"></i>", "en": "<i class=\"fas fa-crown\"></i>"},
            "required_days": 90,
            "confetti_type": "fireworks",
            "sound": "fanfare"
        }
    }
}

def calculate_streak(user):
    """حساب السلسلة (streak) للمستخدم بناءً على الإدخالات اليومية مع التعامل مع النكسة."""
    today = timezone.localdate()
    if not user.start_date:
        user.start_date = today
        user.save()
        print(f"Set start_date for {user.username} to {today}")

    streak = 0
    current_date = today
    max_date = JournalEntry.objects.filter(user=user).aggregate(max_date=Max('entry_date'))['max_date'] or user.start_date
    latest_relapse = JournalEntry.objects.filter(user=user, is_relapse=True).aggregate(max_date=Max('entry_date'))['max_date']

    if latest_relapse is not None and latest_relapse >= user.start_date:
        user.start_date = latest_relapse + timedelta(days=1)
        user.save()
        print(f"Reset start_date to {user.start_date} due to relapse on {latest_relapse}")

    while current_date >= user.start_date:
        if JournalEntry.objects.filter(user=user, entry_date=current_date).exists():
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
        if current_date < user.start_date or streak > 365:
            break

    return streak

@login_required
def dashboard_view(request):
    """
    Displays the user's dashboard, including journal entry form, streak, and progress.
    Handles achievement checking and relapse reporting.
    """
    today = timezone.localdate()
    entry, created = JournalEntry.objects.get_or_create(user=request.user, entry_date=today)

    # حساب السلسلة
    streak = calculate_streak(request.user)

    if request.method == 'POST':
        daily_entry_content = request.POST.get('daily_entry')
        is_relapse = 'is_relapse' in request.POST
        if daily_entry_content or is_relapse:
            entry.content = daily_entry_content or entry.content
            entry.is_relapse = is_relapse
            entry.save()
            if is_relapse:
                messages.warning(request, "لقد سجلت نكسة. لا تيأس، هذه بداية جديدة! تحدث إلى رفيق الدرب أو اطلب الدعم.")
                streak = 0  # إعادة تعيين السلسلة عند النكسة
            else:
                messages.success(request, "تم حفظ يومياتك بنجاح!")
            check_and_unlock_achievements(request.user)
            return redirect('journal:dashboard')
        else:
            messages.error(request, "لا يمكن حفظ يومية فارغة.")

    # فتح الإنجازات الجديدة للنافذة المنبثقة
    unlocked_achievements_for_popup = []
    for ach_category in ["streaks", "milestones", "special"]:
        for ach_id, ach_data in ACHIEVEMENTS_DATA.get(ach_category, {}).items():
            if ach_category == "streaks" and ach_data.get("required_days") and streak >= ach_data["required_days"]:
                if not UserAchievement.objects.filter(user=request.user, achievement_id=ach_id).exists():
                    achievement = UserAchievement.objects.create(user=request.user, achievement_id=ach_id)
                    unlocked_achievements_for_popup.append({
                        "id": ach_id,
                        "title": ach_data["title"],
                        "description": ach_data["message"],
                        "icon": ach_data["badge_icon"],
                        "confetti_type": ach_data.get("confetti_type", "basic"),
                        "sound": ach_data.get("sound", "ding"),
                        "unlocked_at": achievement.unlocked_at.isoformat() if achievement.unlocked_at else None
                    })
            elif ach_category == "milestones" and ach_id == "FIRST_GOAL_COMPLETED":
                if not UserAchievement.objects.filter(user=request.user, achievement_id=ach_id).exists():
                    if JournalEntry.objects.filter(user=request.user).count() == 1:
                        achievement = UserAchievement.objects.create(user=request.user, achievement_id=ach_id)
                        unlocked_achievements_for_popup.append({
                            "id": ach_id,
                            "title": ach_data["title"],
                            "description": ach_data["message"],
                            "icon": ach_data["badge_icon"],
                            "confetti_type": ach_data.get("confetti_type", "basic"),
                            "sound": ach_data.get("sound", "ding"),
                            "unlocked_at": achievement.unlocked_at.isoformat() if achievement.unlocked_at else None
                        })

    # جلب بيانات اليوميات والإنجازات
    journal_entries = JournalEntry.objects.filter(user=request.user).values('entry_date', 'is_relapse')
    journal_entries_processed = [
        {'entry_date': item['entry_date'].isoformat(), 'is_relapse': item['is_relapse']}
        for item in journal_entries
    ]
    print("Journal Entries Processed:", journal_entries_processed)  # نقل الطباعة هنا
    user_achievements = UserAchievement.objects.filter(user=request.user).values('achievement_id', 'unlocked_at')
    user_achievements_processed = [
        {'achievement_id': item['achievement_id'], 'unlocked_at': item['unlocked_at'].isoformat() if item['unlocked_at'] else None}
        for item in user_achievements
    ]

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
        "journal_entries": journal_entries_processed,
        "user_achievements": user_achievements_processed,
    }

    days_passed = 0
    target_days = 90
    if request.user.start_date:
        days_passed = (today - request.user.start_date).days + 1
        if days_passed < 0:
            days_passed = 0
    print(f"Days passed: {days_passed}, Target days: {target_days} for user {request.user.username}")

    character_level = min(streak // 10, 5)

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
    """فحص وفتح الإنجازات بناءً على السلسلة والشروط الأخرى."""
    streak = calculate_streak(user)

    for ach_category in ["streaks", "milestones", "special"]:
        for ach_id, ach_data in ACHIEVEMENTS_DATA.get(ach_category, {}).items():
            if ach_category == "streaks" and ach_data.get("required_days") and streak >= ach_data["required_days"]:
                if not UserAchievement.objects.filter(user=user, achievement_id=ach_id).exists():
                    UserAchievement.objects.create(user=user, achievement_id=ach_id)
                    messages.info(user, f"تم فتح إنجاز جديد: {ach_data['title']['ar']}!")
            elif ach_category == "milestones" and ach_id == "FIRST_GOAL_COMPLETED":
                if not UserAchievement.objects.filter(user=user, achievement_id=ach_id).exists():
                    if JournalEntry.objects.filter(user=user).count() == 1:
                        UserAchievement.objects.create(user=user, achievement_id=ach_id)
                        messages.info(user, f"تم فتح إنجاز جديد: {ach_data['title']['ar']}!")

@login_required
def journal_entries_view(request):
    """عرض جميع إدخالات اليوميات للمستخدم."""
    entries = JournalEntry.objects.filter(user=request.user).order_by('-entry_date')
    return render(request, 'journal/journal_entries.html', {'entries': entries})

@login_required
def goals_view(request):
    """عرض أهداف المستخدم."""
    return render(request, 'journal/goals.html')

@login_required
def companion_view(request):
    """عرض رفيق الدرب."""
    return render(request, 'journal/companion.html')

@login_required
def add_entry_view(request):
    """إضافة إدخال يومي جديد."""
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.entry_date = timezone.localdate()
            entry.save()
            messages.success(request, "تمت إضافة اليومية بنجاح!")
            return redirect('journal:dashboard')
    else:
        form = JournalEntryForm()
    return render(request, 'journal/add_entry.html', {'form': form})

@login_required
def edit_entry_view(request, entry_id):
    """تعديل إدخال يومي موجود."""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل اليومية بنجاح!")
            return redirect('journal:journal_entries')
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'journal/edit_entry.html', {'form': form, 'entry': entry})

@login_required
def delete_entry_view(request, entry_id):
    """حذف إدخال يومي."""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "تم حذف اليومية بنجاح!")
        return redirect('journal:journal_entries')
    return render(request, 'journal/delete_entry.html', {'entry': entry})

@login_required
def achievements_view(request):
    """عرض الإنجازات للمستخدم."""
    achievements = UserAchievement.objects.filter(user=request.user)
    return render(request, 'journal/achievements.html', {'achievements': achievements})

@login_required
def relapse_support_view(request):
    """عرض دعم النكسة."""
    return render(request, 'journal/relapse_support.html')

