# goals/forms.py

from django import forms
from .models import Goal

class GoalForm(forms.ModelForm):
    """
    Form for creating and updating Goal objects.
    """
    class Meta:
        model = Goal
        fields = ['title', 'description', 'target_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'placeholder': 'Enter goal title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out resize-y',
                'rows': 5,
                'placeholder': 'Describe your goal in more detail'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out',
                'type': 'date' # HTML5 date input
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-primary-dark transition duration-200 ease-in-out'
            }),
        }
        labels = {
            'title': 'Goal Title',
            'description': 'Description',
            'target_date': 'Target Date',
            'status': 'Status',
        }

