from django import forms
from .models import Goal

class GoalForm(forms.ModelForm):
    """
    النموذج لإنشاء وتحديث أهداف المستخدم.
    """
    class Meta:
        model = Goal
        fields = ['title', 'description', 'target_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'أدخل عنوان الهدف'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
                'rows': 5,
                'placeholder': 'اشرح هدفك بمزيد من التفاصيل'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'type': 'date'  # مدخل التاريخ HTML5
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
            }),
        }
        labels = {
            'title': 'عنوان الهدف',
            'description': 'الوصف',
            'target_date': 'التاريخ المستهدف',
            'status': 'الحالة',
        }
