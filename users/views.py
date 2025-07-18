# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import AnonymousUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = AnonymousUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # تسجيل دخول المستخدم تلقائياً بعد التسجيل
            return redirect('dashboard') # توجيهه إلى لوحة التحكم
    else:
        form = AnonymousUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})