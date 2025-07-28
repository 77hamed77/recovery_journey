# community/forms.py

from django import forms
from .models import Post, Comment, Message, Report # تأكد من استيراد كل النماذج اللازمة
import markdown2 # لاستخدام Markdown
from django.utils.translation import gettext_lazy as _ # للترجمة في الفورم

class PostForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل المنشورات في المجتمع.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-4 text-lg focus:outline-none focus:ring-4 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
            'rows': 8,
            'placeholder': _('ما الذي تفكر فيه اليوم؟ شاركنا أفكارك (يمكنك استخدام تنسيق Markdown)...')
        }),
        label=_("محتوى المنشور")
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-lg focus:outline-none focus:ring-4 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
            'placeholder': _('عنوان المنشور...')
        }),
        label=_("عنوان المنشور")
    )

    class Meta:
        model = Post
        fields = ['title', 'content'] # تأكد من أن الحقول هنا مطابقة لنموذج Post

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تخصيص Widgets لجميع الحقول إذا لزم الأمر بشكل إضافي
        for name, field in self.fields.items():
            if name == 'title':
                field.widget.attrs.update({'aria-label': _('عنوان المنشور')})
            elif name == 'content':
                field.widget.attrs.update({'aria-label': _('محتوى المنشور')})


class CommentForm(forms.ModelForm):
    """
    نموذج لإنشاء التعليقات.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
            'rows': 3,
            'placeholder': _('اكتب تعليقك هنا (يمكنك استخدام تنسيق Markdown)...')
        }),
        label=_("محتوى التعليق")
    )

    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'aria-label': _('محتوى التعليق')})


class MessageForm(forms.ModelForm): # <-- هذا هو تعريف MessageForm
    """
    نموذج لإنشاء الرسائل الخاصة.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
            'rows': 3,
            'placeholder': _('اكتب رسالتك هنا...')
        }),
        label=_("محتوى الرسالة")
    )

    class Meta:
        model = Message
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'aria-label': _('محتوى الرسالة')})


class ReportForm(forms.ModelForm):
    """
    نموذج للإبلاغ عن المحتوى.
    """
    reason = forms.ChoiceField(
        choices=Report.REASON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
        }),
        label=_("سبب البلاغ")
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-base focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
            'rows': 4,
            'placeholder': _('تفاصيل إضافية (اختياري)...')
        }),
        label=_("وصف إضافي")
    )

    class Meta:
        model = Report
        fields = ['reason', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs.update({'aria-label': _('سبب البلاغ')})
        self.fields['description'].widget.attrs.update({'aria-label': _('وصف إضافي للبلاغ')})

