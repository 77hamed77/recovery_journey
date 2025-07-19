# journal/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # استيراد timezone

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="المحتوى")
    # هذا الحقل سيخزن تاريخ اليوم فقط، ويضمن أن كل مستخدم له إدخال واحد فقط في اليوم
    entry_date = models.DateField(default=timezone.now, unique_for_date="entry_date") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"يومية لـ {self.user.username} في {self.entry_date}"

    class Meta:
        ordering = ['-entry_date']
        
class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement_id = models.CharField(max_length=100, verbose_name="معرف الإنجاز")
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفتح")

    class Meta:
        verbose_name = "إنجاز المستخدم"
        verbose_name_plural = "إنجازات المستخدمين"
        # منع المستخدم من الحصول على نفس الإنجاز مرتين
        unique_together = ('user', 'achievement_id')

    def __str__(self):
        return f"إنجاز {self.achievement_id} للمستخدم {self.user.username}"