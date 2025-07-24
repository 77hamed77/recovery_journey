# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date

# استيراد النماذج المخصصة والفورمات
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm, CustomPasswordChangeForm, SetStartDateForm # تم إضافة SetStartDateForm
from .models import CustomUser, Profile # تم إزالة JournalEntry من هنا
from journal.models import JournalEntry # تم إضافة: استيراد JournalEntry من تطبيقه الصحيح

def register_view(request):
    """
    معالجة طلبات إنشاء حساب جديد.
    """
    if request.user.is_authenticated:
        messages.info(request, "أنت مسجل الدخول بالفعل.")
        return redirect('journal:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # لا يتم تسجيل الدخول تلقائياً، بل يتم التوجيه إلى صفحة تسجيل الدخول.
            messages.success(request, f'تم إنشاء حسابك بنجاح يا {user.username}! يمكنك الآن تسجيل الدخول.')
            return redirect('login') 
        else:
            messages.error(request, "حدثت أخطاء في النموذج. الرجاء مراجعة البيانات المدخلة.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    معالجة طلبات تسجيل الدخول.
    """
    if request.user.is_authenticated:
        messages.info(request, "أنت مسجل الدخول بالفعل.")
        return redirect('journal:dashboard')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            messages.success(request, f'مرحباً بعودتك يا {user.username}!')
            # تحقق مما إذا كان المستخدم لديه تاريخ بدء محدد
            if user.start_date is None:
                return redirect('set_start_date') # توجيه لتعيين تاريخ البدء
            return redirect('journal:dashboard') # توجيه إلى لوحة التحكم
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة. الرجاء المحاولة مرة أخرى.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    معالجة طلب تسجيل الخروج. يتطلب طلب POST للأمان.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, "تم تسجيل الخروج بنجاح. نتمنى لك يوماً سعيداً!")
    return redirect('login') # توجيه إلى صفحة تسجيل الدخول بعد تسجيل الخروج (سواء POST أو GET غير متوقع)


@login_required
def settings_view(request):
    """
    عرض وتحديث إعدادات الملف الشخصي للمستخدم.
    """
    # تأكد من وجود ملف شخصي للمستخدم. إذا لم يكن موجوداً، قم بإنشائه.
    # هذا يضمن أن المستخدم الذي تم إنشاؤه قبل إضافة Profile model لن يواجه مشكلة.
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ التغييرات بنجاح!')
            return redirect('settings')
        else:
            messages.error(request, "حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.")
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/settings.html', {'form': form})


@login_required
def set_start_date_view(request):
    """
    معالجة طلب تعيين تاريخ بدء رحلة التعافي للمستخدم.
    """
    user = request.user
    if request.method == 'POST':
        form = SetStartDateForm(request.POST, instance=user) # استخدام SetStartDateForm
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعيين تاريخ بدء رحلتك بنجاح!")
            return redirect('journal:dashboard')
        else:
            messages.error(request, "حدث خطأ أثناء تعيين تاريخ البدء. الرجاء مراجعة البيانات المدخلة.")
    else:
        form = SetStartDateForm(instance=user) # تهيئة الفورم مع البيانات الموجودة
    
    return render(request, 'users/set_start_date.html', {'form': form})


@login_required
def delete_account_view(request):
    """
    معالجة طلب حذف الحساب.
    """
    if request.method == 'POST':
        password = request.POST.get('password')
        if request.user.check_password(password):
            # حذف اليوميات المرتبطة بالمستخدم أولاً
            # JournalEntry يتم استيراده الآن من journal.models
            JournalEntry.objects.filter(user=request.user).delete()
            # ثم حذف المستخدم نفسه
            request.user.delete()
            logout(request)
            messages.success(request, "تم حذف حسابك وجميع بياناتك بنجاح. نأمل أن تعود قريباً!")
            return redirect('login') # توجيه إلى صفحة تسجيل الدخول بعد الحذف
        else:
            messages.error(request, 'كلمة المرور غير صحيحة. الرجاء المحاولة مرة أخرى.')
            return render(request, 'users/delete_account.html')
    else:
        return render(request, 'users/delete_account.html')

@login_required
def my_journal_view(request):
    """
    عرض سجل يوميات المستخدم.
    """
    # JournalEntry يتم استيراده الآن من journal.models
    entries = JournalEntry.objects.filter(user=request.user).order_by('-entry_date') # تم التصحيح إلى '-entry_date'
    return render(request, 'users/my_journal.html', {'entries': entries})

@login_required
def password_change_view(request):
    """
    معالجة طلب تغيير كلمة المرور.
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # مهم لتحديث جلسة المستخدم بعد تغيير كلمة المرور
            messages.success(request, 'تم تغيير كلمة المرور بنجاح!')
            return redirect('settings')
        else:
            messages.error(request, "حدث خطأ أثناء تغيير كلمة المرور. الرجاء مراجعة البيانات المدخلة.")
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'users/password_change.html', {'form': form})

