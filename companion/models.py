# companion/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_text = models.TextField(verbose_name="رسالة المستخدم")
    response_text = models.TextField(verbose_name="رد الروبوت")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="التوقيت")

    def __str__(self):
        return f"رسالة من {self.user.username} في {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "رسالة محادثة"
        verbose_name_plural = "رسائل المحادثات"
        ordering = ['timestamp'] # ترتيب الرسائل حسب التوقيت