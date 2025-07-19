# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class AnonymousUserCreationForm(UserCreationForm):
    """
    نموذج مخصص لإنشاء مستخدم جديد يطلب فقط اسم المستخدم وكلمة المرور.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        # نحدد الحقول المطلوبة فقط، حقول كلمة المرور تضاف تلقائياً
        fields = ('username',)

class ProfileUpdateForm(forms.ModelForm):
    """
    نموذج لتحديث إعدادات الملف الشخصي للمستخدم.
    """
    # استخدام RadioSelect يجعل الخيارات أوضح للمستخدم
    content_preference = forms.ChoiceField(
        choices=Profile.THEME_CHOICES,
        widget=forms.RadioSelect,
        label="تفضيلات المحتوى"
    )

    class Meta:
        model = Profile
        fields = ['content_preference']