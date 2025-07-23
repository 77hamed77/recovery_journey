from django import forms
from .models import Resource, ContactMessage

class ContactMessageForm(forms.ModelForm):
    """
    نموذج المستخدم لإرسال رسالة تواصل إلى الطبيب النفسي.
    """
    class Meta:
        model = ContactMessage
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'موضوع رسالتك'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
                'rows': 6,
                'placeholder': 'اكتب رسالتك هنا...'
            }),
        }
        labels = {
            'subject': 'الموضوع',
            'message': 'الرسالة',
        }


class AdminReplyForm(forms.ModelForm):
    """
    نموذج للأدمن (الطبيب النفسي) لكتابة الرد على رسالة تواصل.
    """
    class Meta:
        model = ContactMessage
        fields = ['reply']
        widgets = {
            'reply': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
                'rows': 6,
                'placeholder': 'اكتب ردك هنا...'
            }),
        }
        labels = {
            'reply': 'الرد',
        }


class ResourceForm(forms.ModelForm):
    """
    نموذج لإنشاء وتحديث الموارد.
    """
    class Meta:
        model = Resource
        fields = ['title', 'description', 'url', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'أدخل عنوان المورد'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
                'rows': 5,
                'placeholder': 'اشرح المورد بمزيد من التفاصيل'
            }),
            'url': forms.URLInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'مثال: https://example.com/article'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
            }),
        }
        labels = {
            'title': 'عنوان المورد',
            'description': 'الوصف',
            'url': 'رابط المورد',
            'file': 'رفع ملف',
        }
        help_texts = {
            'url': 'يرجى إضافة رابط لمصدر خارجي (إن وجد).',
            'file': 'قم برفع مستند (PDF، DOCX، TXT، إلخ). يمكنك إضافة رابط أو ملف أو كليهما.',
        }

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        file = cleaned_data.get('file')

        if not url and not file:
            raise forms.ValidationError(
                "يجب إضافة رابط أو رفع ملف لإتمام إرسال المورد."
            )
        return cleaned_data
