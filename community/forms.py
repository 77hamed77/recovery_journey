# community/forms.py

from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    """
    نموذج لإنشاء وتعديل منشورات المجتمع.
    """
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-lg focus:outline-none focus:ring-4 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'عنوان المنشور...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-lg focus:outline-none focus:ring-4 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y h-40',
                'placeholder': 'اكتب محتوى منشورك هنا...'
            }),
        }
        labels = {
            'title': 'العنوان',
            'content': 'المحتوى',
        }

class CommentForm(forms.ModelForm):
    """
    نموذج لإنشاء تعليقات على المنشورات.
    """
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 text-base focus:outline-none focus:ring-4 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y h-24',
                'placeholder': 'اكتب تعليقك هنا...'
            }),
        }
        labels = {
            'content': 'تعليقك',
        }

