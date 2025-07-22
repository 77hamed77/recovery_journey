# info/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ContactForm, ResourceForm
from .models import Resource

# Test function to check if the user is a superuser (for resource management)
def is_superuser(user):
    return user.is_superuser

def about_view(request):
    """
    Displays the "About Us" page.
    """
    return render(request, 'info/about.html')

def privacy_view(request):
    """
    Displays the "Privacy Policy and Terms of Service" page.
    """
    return render(request, 'info/privacy.html')

def contact_view(request):
    """
    Handles and displays the "Contact Us" page.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            try:
                send_mail(
                    f'Message from Recovery Journey: {subject}', # Subject
                    f'Sender: {name} <{email}>\n\nMessage:\n{message}', # Message body
                    settings.DEFAULT_FROM_EMAIL, # From email (must be configured in settings.py)
                    [settings.CONTACT_EMAIL], # To email (must be configured in settings.py)
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
                return redirect('info:contact') # Redirect to prevent resubmission
            except Exception as e:
                messages.error(request, f'An error occurred while sending your message. Please try again later. ({e})')
    else:
        form = ContactForm()
    
    return render(request, 'info/contact.html', {'form': form})

# ===================================================================
# Resource Management Views (Requires Superuser Privileges)
# ===================================================================

def resources_list_view(request):
    """
    Displays a list of all resources.
    """
    resources = Resource.objects.all().order_by('-created_at')
    context = {
        'resources': resources,
    }
    return render(request, 'info/resources.html', context)

def resource_detail_view(request, pk):
    """
    Displays the details of a specific resource.
    """
    resource = get_object_or_404(Resource, pk=pk)
    context = {
        'resource': resource,
    }
    return render(request, 'info/resource_detail.html', context)

@login_required
@user_passes_test(is_superuser)
def resource_create_view(request):
    """
    Handles the creation of a new resource (superuser only).
    """
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user # Assign the creating user
            resource.save()
            messages.success(request, 'Resource created successfully!')
            return redirect('info:resources_list')
    else:
        form = ResourceForm()
    
    context = {
        'form': form,
        'page_title': 'Add New Resource',
        'submit_button_text': 'Add Resource',
    }
    return render(request, 'info/resource_form.html', context)

@login_required
@user_passes_test(is_superuser)
def resource_edit_view(request, pk):
    """
    Handles the editing of an existing resource (superuser only).
    """
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('info:resource_detail', pk=resource.pk)
    else:
        form = ResourceForm(instance=resource)
    
    context = {
        'form': form,
        'resource': resource,
        'page_title': f'Edit Resource: {resource.title}',
        'submit_button_text': 'Update Resource',
    }
    return render(request, 'info/resource_form.html', context)

@login_required
@user_passes_test(is_superuser)
def resource_confirm_delete_view(request, pk):
    """
    Displays a confirmation page before deleting a resource (superuser only).
    """
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully!')
        return redirect('info:resources_list')
    context = {
        'resource': resource,
    }
    return render(request, 'info/resource_confirm_delete.html', context)

