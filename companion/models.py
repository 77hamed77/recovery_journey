# companion/models.py
from django.db import models
from django.conf import settings # <-- إضافة هذا الاستيراد

class ChatMessage(models.Model):
    # استخدام settings.AUTH_USER_MODEL بدلاً من User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User")
    message = models.TextField(verbose_name="Message")
    response = models.TextField(blank=True, verbose_name="Response")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"Message from {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

