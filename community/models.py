# community/models.py

from django.db import models
from django.conf import settings # لاستيراد نموذج المستخدم المخصص
from django.utils import timezone

class Post(models.Model):
    """
    نموذج يمثل منشورًا في المجتمع.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts', verbose_name="المستخدم")
    title = models.CharField(max_length=200, verbose_name="عنوان المنشور")
    content = models.TextField(verbose_name="محتوى المنشور")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ آخر تعديل")

    class Meta:
        verbose_name = "منشور المجتمع"
        verbose_name_plural = "منشورات المجتمع"
        ordering = ['-created_at'] # ترتيب المنشورات من الأحدث للأقدم

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """يعيد الـ URL الكانفاس لتفاصيل المنشور."""
        from django.urls import reverse
        return reverse('community:post_detail', args=[str(self.id)])

class Comment(models.Model):
    """
    نموذج يمثل تعليقًا على منشور معين.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="المنشور")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comments', verbose_name="المستخدم")
    content = models.TextField(verbose_name="محتوى التعليق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "تعليق المجتمع"
        verbose_name_plural = "تعليقات المجتمع"
        ordering = ['created_at'] # ترتيب التعليقات من الأقدم للأحدث

    def __str__(self):
        return f"تعليق من {self.user.username} على {self.post.title[:50]}..."

