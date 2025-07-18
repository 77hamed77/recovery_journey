# users/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AnonymousUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',) # نطلب اسم المستخدم فقط
        