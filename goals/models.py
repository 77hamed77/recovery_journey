from django.db import models
from django.conf import settings
from django.utils import timezone

class Goal(models.Model):
    """
    النموذج الذي يمثّل هدفًا واحدًا للمستخدم.
    """
    # ربط الهدف بالمستخدم
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name="المستخدم"
    )
    
    title = models.CharField(max_length=200, verbose_name="عنوان الهدف")
    description = models.TextField(blank=True, verbose_name="الوصف")
    target_date = models.DateField(null=True, blank=True, verbose_name="التاريخ المستهدف")
    
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="الحالة"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "هدف"
        verbose_name_plural = "أهداف"

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @property
    def is_overdue(self):
        if self.target_date and self.target_date < timezone.localdate() and self.status not in ['completed', 'cancelled']:
            return True
        return False

    @property
    def progress_status(self):
        if self.status == 'completed':
            return "مكتمل"
        elif self.status == 'cancelled':
            return "ملغي"
        elif self.is_overdue:
            return "متأخر"
        elif self.status == 'in_progress':
            return "قيد التنفيذ"
        else:
            return "قيد الانتظار"
