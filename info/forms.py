# info/forms.py

from django import forms
from .models import Resource

class ContactForm(forms.Form):
    """
    Simple form for the contact us page.
    """
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
            'placeholder': 'Your Full Name'
        }),
        label="Name"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
            'placeholder': 'Your Email Address'
        }),
        label="Email"
    )
    subject = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
            'placeholder': 'Subject of your message'
        }),
        label="Subject"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
            'rows': 6,
            'placeholder': 'Write your message here...'
        }),
        label="Message"
    )

class ResourceForm(forms.ModelForm):
    """
    Form for creating and updating Resource objects.
    """
    class Meta:
        model = Resource
        fields = ['title', 'description', 'url', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'Enter resource title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
                'rows': 5,
                'placeholder': 'Describe the resource in more detail'
            }),
            'url': forms.URLInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'e.g., https://example.com/article'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
            }),
        }
        labels = {
            'title': 'Resource Title',
            'description': 'Description',
            'url': 'URL Link',
            'file': 'Upload File',
        }
        help_texts = {
            'url': 'Provide a link to an external resource.',
            'file': 'Upload a document (PDF, DOCX, TXT, etc.). You can provide either a link or a file, or both.',
        }

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        file = cleaned_data.get('file')

        if not url and not file:
            # Add a non-field error if neither URL nor file is provided
            raise forms.ValidationError(
                "You must provide either a URL link or upload a file for the resource."
            )
        return cleaned_data

