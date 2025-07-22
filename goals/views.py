# goals/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Goal
from .forms import GoalForm

@login_required
def goals_list(request):
    """
    Displays a list of all goals for the current user.
    """
    user_goals = Goal.objects.filter(user=request.user).order_by('status', 'target_date')
    context = {
        'goals': user_goals,
    }
    return render(request, 'goals/goals_list.html', context)

@login_required
def goal_detail(request, pk):
    """
    Displays the details of a specific goal.
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    context = {
        'goal': goal,
    }
    return render(request, 'goals/goal_detail.html', context)

@login_required
def goal_create(request):
    """
    Handles the creation of a new goal.
    """
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal created successfully!')
            return redirect('goals:goals_list') # Redirect to the goals list
    else:
        form = GoalForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Goal',
        'submit_button_text': 'Create Goal',
    }
    return render(request, 'goals/goal_form.html', context) # Reusing goal_form.html for create

@login_required
def goal_edit(request, pk):
    """
    Handles the editing of an existing goal.
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('goals:goal_detail', pk=goal.pk) # Redirect to goal detail
    else:
        form = GoalForm(instance=goal)
    
    context = {
        'form': form,
        'goal': goal,
        'page_title': f'Edit Goal: {goal.title}',
        'submit_button_text': 'Update Goal',
    }
    return render(request, 'goals/goal_form.html', context) # Reusing goal_form.html for edit

@login_required
def goal_confirm_delete(request, pk):
    """
    Displays a confirmation page before deleting a goal.
    """
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
        return redirect('goals:goals_list')
    context = {
        'goal': goal,
    }
    return render(request, 'goals/goal_confirm_delete.html', context)

