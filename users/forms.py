from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import CustomUser, Profile # تأكد من استيراد Profile

class CustomUserCreationForm(UserCreationForm):
    """
    نموذج مخصص لإنشاء مستخدم جديد.
    يتضمن اسم المستخدم وكلمة المرور وتأكيد كلمة المرور.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # هنا نحدد الحقول التي نريدها. 'username' هو حقلنا المخصص.
        # UserCreationForm يوفر تلقائياً حقلي 'password' و 'password2' (تأكيد كلمة المرور).
        # لذا، لا نحتاج لتضمينها صراحة هنا إذا كنا نعتمد على سلوك UserCreationForm الافتراضي.
        # إذا قمت بتضمين 'password' و 'password2' هنا، فهذا هو سبب التكرار.
        # الطريقة الصحيحة هي تحديد الحقول التي تضافها أنت، و UserCreationForm سيتعامل مع البقية.
        fields = ('username',) # فقط اسم المستخدم، UserCreationForm سيتعامل مع كلمات المرور

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة فئات Tailwind CSS للحقول لضمان التناسق البصري
        # يجب أن نطبق الأنماط على جميع الحقول التي يتم إنشاؤها بواسطة النموذج (بما في ذلك حقول كلمة المرور من النموذج الأساسي)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
            })
            # إضافة placeholder للحقول
            if field_name == 'username':
                self.fields[field_name].widget.attrs['placeholder'] = 'اختر اسم مستخدم فريد'
            elif field_name == 'password': # هذا سيطبق على حقل كلمة المرور الأول
                self.fields[field_name].widget.attrs['placeholder'] = 'كلمة مرور بسيطة وسهلة التذكر'
            elif field_name == 'password2': # هذا سيطبق على حقل تأكيد كلمة المرور
                self.fields[field_name].widget.attrs['placeholder'] = 'أعد إدخال كلمة المرور'


class CustomAuthenticationForm(AuthenticationForm):
    """
    نموذج مخصص لتسجيل الدخول.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة فئات Tailwind CSS للحقول لضمان التناسق البصري
        self.fields['username'].widget.attrs.update({
            'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
            'placeholder': 'اسم المستخدم الخاص بك'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
            'placeholder': 'كلمة المرور الخاصة بك'
        })

class ProfileUpdateForm(forms.ModelForm):
    """
    نموذج لتحديث إعدادات الملف الشخصي للمستخدم.
    """
    content_preference = forms.ChoiceField(
        choices=Profile.THEME_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-radio text-blue-600 h-4 w-4'}), # أضف فئات Tailwind للـ radio buttons
        label="تفضيلات المحتوى"
    )

    class Meta:
        model = Profile
        fields = ['content_preference']

class CustomPasswordChangeForm(PasswordChangeForm):
    """
    نموذج مخصص لتغيير كلمة المرور مع تحسينات Tailwind.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
            })

# النموذج الجديد لتعيين تاريخ البدء
class SetStartDateForm(forms.ModelForm):
    """
    نموذج لتعيين أو تحديث تاريخ بدء رحلة التعافي للمستخدم.
    """
    class Meta:
        model = CustomUser
        fields = ['start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
            }),
        }
        labels = {
            'start_date': 'تاريخ بدء رحلة التعافي',
        }

