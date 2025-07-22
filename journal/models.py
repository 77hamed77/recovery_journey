from django.db import models
from django.conf import settings
from django.utils import timezone

class JournalEntry(models.Model):
    """
    نموذج يمثل إدخال يومية واحد لمستخدم معين.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries', verbose_name="المستخدم")
    content = models.TextField(verbose_name="المحتوى")
    entry_date = models.DateField(default=timezone.now, verbose_name="تاريخ اليومية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        ordering = ['-entry_date']
        unique_together = ('user', 'entry_date')
        verbose_name = "يومية"
        verbose_name_plural = "يوميات"

    def __str__(self):
        return f"يومية لـ {self.user.username} في {self.entry_date}"

class Achievement(models.Model):
    """
    نموذج يمثل إنجازًا يمكن للمستخدم تحقيقه.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements_list', verbose_name="المستخدم")
    title = models.CharField(max_length=200, verbose_name="عنوان الإنجاز")
    description = models.TextField(verbose_name="وصف الإنجاز")
    icon = models.CharField(max_length=100, blank=True, verbose_name="أيقونة الإنجاز")  # لأيقونة الشارة
    unlocked = models.BooleanField(default=False, verbose_name="تم الفتح")
    unlocked_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الفتح")
    required_days = models.IntegerField(null=True, blank=True, verbose_name="الأيام المطلوبة")  # لإنجازات السلاسل
    type = models.CharField(
        max_length=50,
        choices=[
            ('streak', 'Streak'),
            ('milestone', 'Milestone'),
            ('special', 'Special')
        ],
        verbose_name="نوع الإنجاز"
    )

    class Meta:
        verbose_name = "إنجاز"
        verbose_name_plural = "إنجازات"
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class UserAchievement(models.Model):
    """
    نموذج يمثل إنجازًا حققه مستخدم معين.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_achievements', verbose_name="المستخدم")
    achievement_id = models.CharField(max_length=100, verbose_name="معرف الإنجاز")  # يمكن تحسينه ليكون ForeignKey إلى Achievement
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفتح")

    class Meta:
        verbose_name = "إنجاز المستخدم"
        verbose_name_plural = "إنجازات المستخدمين"
        unique_together = ('user', 'achievement_id')
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"إنجاز {self.achievement_id} للمستخدم {self.user.username}"