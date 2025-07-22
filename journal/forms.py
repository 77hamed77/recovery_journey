# journal/forms.py

from django import forms
from .models import JournalEntry

class JournalEntryForm(forms.ModelForm):
    """
    نموذج لتعديل إدخالات اليوميات.
    """
    class Meta:
        model = JournalEntry
        fields = ['content'] # الحقل الذي تريد تعديله في اليومية
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-4 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'rows': 8,
                'placeholder': 'اكتب يومياتك هنا...'
            }),
        }
        labels = {
            'content': 'محتوى اليومية',
        }

