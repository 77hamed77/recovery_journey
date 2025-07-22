# goals/models.py

from django.db import models
from django.conf import settings # <-- إضافة هذا الاستيراد
from django.utils import timezone

class Goal(models.Model):
    """
    Model representing a single goal for a user.
    """
    # Foreign Key to the User model. If a user is deleted, their goals are also deleted.
    # استخدام settings.AUTH_USER_MODEL بدلاً من User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals', verbose_name="User")
    
    # Title of the goal
    title = models.CharField(max_length=200, verbose_name="Title")
    
    # Description of the goal
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Target date for the goal (optional)
    target_date = models.DateField(null=True, blank=True, verbose_name="Target Date")
    
    # Status of the goal (e.g., 'pending', 'in_progress', 'completed', 'cancelled')
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    
    # Date when the goal was created
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    
    # Date when the goal was last updated
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated At")

    class Meta:
        # Default ordering for goals: newest first
        ordering = ['-created_at']
        verbose_name = "Goal"
        verbose_name_plural = "Goals"

    def __str__(self):
        """String representation of the Goal model."""
        return f"{self.title} by {self.user.username}"

    @property
    def is_overdue(self):
        """Checks if the goal is overdue but not completed or cancelled."""
        if self.target_date and self.target_date < timezone.localdate() and self.status not in ['completed', 'cancelled']:
            return True
        return False

    @property
    def progress_status(self):
        """Returns a human-readable progress status."""
        if self.status == 'completed':
            return "Completed"
        elif self.status == 'cancelled':
            return "Cancelled"
        elif self.is_overdue:
            return "Overdue"
        elif self.status == 'in_progress':
            return "In Progress"
        else:
            return "Pending"

