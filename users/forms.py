# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AnonymousUserCreationForm, ProfileUpdateForm

def register_view(request):
    """
    معالجة طلبات إنشاء حساب جديد.
    """
    if request.user.is_authenticated:
        return redirect('dashboard') # إذا كان المستخدم مسجلاً بالفعل، يتم توجيهه للوحة التحكم

    if request.method == 'POST':
        form = AnonymousUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # تسجيل دخول المستخدم تلقائياً بعد التسجيل
            messages.success(request, f'أهلاً بك يا {user.username}! تم إنشاء حسابك بنجاح.')
            return redirect('dashboard') # توجيهه إلى لوحة التحكم
    else:
        form = AnonymousUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    معالجة طلبات تسجيل الدخول.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            # رسالة خطأ إذا كانت البيانات غير صحيحة
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    معالجة طلب تسجيل الخروج. يتطلب طلب POST للأمان.
    """
    if request.method == 'POST':
        logout(request)
        return redirect('login') # توجيهه إلى صفحة الدخول بعد الخروج
    # إذا كان الطلب GET، يتم توجيهه للوحة التحكم
    return redirect('dashboard')


@login_required
def settings_view(request):
    """
    عرض وتحديث إعدادات الملف الشخصي للمستخدم.
    """
    if request.method == 'POST':
        # نمرر 'instance' ليتم تحديث الملف الشخصي الحالي بدلاً من إنشاء واحد جديد
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ التغييرات بنجاح!')
            return redirect('settings')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/settings.html', {'form': form})