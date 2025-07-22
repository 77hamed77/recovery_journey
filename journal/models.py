# journal/models.py

from django.db import models
from django.conf import settings # <-- إضافة هذا الاستيراد
from django.utils import timezone # استيراد timezone

class JournalEntry(models.Model):
    """
    نموذج يمثل إدخال يومية واحد لمستخدم معين.
    """
    # ربط إدخال اليومية بمستخدم معين. عند حذف المستخدم، يتم حذف جميع يومياته.
    # استخدام settings.AUTH_USER_MODEL بدلاً من User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries', verbose_name="المستخدم")
    content = models.TextField(verbose_name="المحتوى") # محتوى اليومية الفعلي
    # هذا الحقل سيخزن تاريخ اليوم فقط، ويضمن أن كل مستخدم له إدخال واحد فقط في اليوم
    entry_date = models.DateField(default=timezone.now, verbose_name="تاريخ اليومية")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء") # يسجل وقت إنشاء الإدخال تلقائياً

    class Meta:
        # تحديد ترتيب الافتراضي للاستعلامات: الأحدث أولاً.
        ordering = ['-entry_date']
        # ضمان أن كل مستخدم يمكنه كتابة إدخال واحد فقط في اليوم المحدد.
        # هذا يكمل `unique_for_date` لتوفير قيد فريد أكثر صرامة على مستوى قاعدة البيانات.
        unique_together = ('user', 'entry_date')
        verbose_name = "يومية"
        verbose_name_plural = "يوميات"

    def __str__(self):
        """تمثيل السلسلة للنموذج."""
        return f"يومية لـ {self.user.username} في {self.entry_date}"

class UserAchievement(models.Model):
    """
    نموذج يمثل إنجازًا حققه مستخدم معين.
    """
    # ربط الإنجاز بمستخدم معين. عند حذف المستخدم، يتم حذف إنجازاته.
    # استخدام settings.AUTH_USER_MODEL بدلاً من User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements', verbose_name="المستخدم")
    achievement_id = models.CharField(max_length=100, verbose_name="معرف الإنجاز") # معرف فريد للإنجاز (مثال: "FIRST_ENTRY_UNLOCKED")
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفتح") # يسجل وقت فتح الإنجاز تلقائياً

    class Meta:
        verbose_name = "إنجاز المستخدم"
        verbose_name_plural = "إنجازات المستخدمين"
        # منع المستخدم من الحصول على نفس الإنجاز مرتين
        unique_together = ('user', 'achievement_id')
        # ترتيب الإنجازات حسب تاريخ الفتح (الأحدث أولاً)
        ordering = ['-unlocked_at']

    def __str__(self):
        """تمثيل السلسلة للنموذج."""
        return f"إنجاز {self.achievement_id} للمستخدم {self.user.username}"

