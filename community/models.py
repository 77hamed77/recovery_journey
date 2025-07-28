# community/models.py

from django.db import models
from django.conf import settings # لاستيراد نموذج المستخدم المخصص
from django.utils import timezone
from django.db.models.functions import Lower # لاستخدامها في UniqueTogether
from django.contrib.contenttypes.models import ContentType 
from django.contrib.contenttypes.fields import GenericForeignKey 

class Post(models.Model):
    """
    نموذج يمثل منشورًا في المجتمع.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts', verbose_name="المستخدم")
    title = models.CharField(max_length=200, verbose_name="عنوان المنشور")
    content = models.TextField(verbose_name="محتوى المنشور") # سيتم تخزين Markdown هنا
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
    
    @property
    def get_likes_count(self):
        # التأكد من جلب Likes المرتبطة بهذا المنشور
        return self.likes.count() # خاصية لحساب عدد الإعجابات

class Comment(models.Model):
    """
    نموذج يمثل تعليقًا على منشور معين، مع دعم الردود المتداخلة.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="المنشور")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comments', verbose_name="المستخدم")
    content = models.TextField(verbose_name="محتوى التعليق") # سيتم تخزين Markdown هنا
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    # حقل لربط التعليق بالتعليق الأم (للردود المتداخلة)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="تعليق أم")

    class Meta:
        verbose_name = "تعليق المجتمع"
        verbose_name_plural = "تعليقات المجتمع"
        ordering = ['created_at'] # ترتيب التعليقات من الأقدم للأحدث

    def __str__(self):
        return f"تعليق من {self.user.username} على {self.post.title[:50]}..."
    
    @property
    def get_likes_count(self):
        # التأكد من جلب Likes المرتبطة بهذا التعليق
        return self.likes.count() # خاصية لحساب عدد الإعجابات


class Like(models.Model):
    """
    نموذج يمثل إعجابًا بمنشور أو تعليق.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes', verbose_name="المستخدم")
    
    # GenericForeignKey لربط الإعجاب بالمنشور أو التعليق
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) 
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') 
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإعجاب")

    class Meta:
        verbose_name = "إعجاب"
        verbose_name_plural = "إعجابات"
        # ضمان أن المستخدم لا يستطيع الإعجاب بنفس العنصر مرتين
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} أعجب بـ {self.content_object}"

class Follow(models.Model):
    """
    نموذج يمثل متابعة مستخدم لمستخدم آخر.
    """
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following', verbose_name="المتابع")
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers', verbose_name="المتابع له")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المتابعة")

    class Meta:
        verbose_name = "متابعة"
        verbose_name_plural = "متابعات"
        # ضمان أن المستخدم لا يستطيع متابعة نفس الشخص مرتين
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} يتابع {self.followed.username}"

class Conversation(models.Model):
    """
    نموذج يمثل محادثة خاصة بين مستخدمين.
    """
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations', verbose_name="المشاركون")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ آخر تحديث")

    class Meta:
        verbose_name = "محادثة"
        verbose_name_plural = "محادثات"
        ordering = ['-updated_at']

    def __str__(self):
        return f"محادثة بين {', '.join([p.username for p in self.participants.all()])}"
    
    # تمت إزالة unique_together من هنا لأنه لا يعمل مباشرة مع ManyToManyField
    # بدلاً من ذلك، يجب التعامل مع تكرار المحادثات في الـ View (start_new_conversation_view)


class Message(models.Model):
    """
    نموذج يمثل رسالة داخل محادثة خاصة.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name="المحادثة")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="المرسل")
    content = models.TextField(verbose_name="محتوى الرسالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    is_read = models.BooleanField(default=False, verbose_name="تمت القراءة")

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "رسائل" # <-- تم التصحيح هنا من verbose_plural
        ordering = ['created_at'] # ترتيب الرسائل من الأقدم للأحدث

    def __str__(self):
        return f"رسالة من {self.sender.username} في محادثة {self.conversation.id}"

class Report(models.Model):
    """
    نموذج يمثل بلاغًا عن محتوى (منشور أو تعليق).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_content', verbose_name="المبلغ")
    
    # GenericForeignKey لربط البلاغ بالمنشور أو التعليق
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) 
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') 
    
    REASON_CHOICES = [
        ('offensive', 'محتوى مسيء / لغة بذيئة'),
        ('spam', 'محتوى غير مرغوب فيه / إعلانات'),
        ('hate_speech', 'خطاب كراهية / تحريض'),
        ('self_harm', 'دعوة لإيذاء النفس'),
        ('misleading', 'معلومات مضللة / كاذبة'),
        ('other', 'أخرى (يرجى التوضيح)'),
    ]
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, verbose_name="سبب البلاغ")
    description = models.TextField(blank=True, null=True, verbose_name="وصف إضافي")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ البلاغ")
    is_resolved = models.BooleanField(default=False, verbose_name="تم الحل")

    class Meta:
        verbose_name = "بلاغ عن محتوى"
        verbose_name_plural = "بلاغات عن محتوى"
        ordering = ['-created_at']
        # لمنع البلاغات المكررة لنفس المستخدم على نفس العنصر
        unique_together = ('user', 'content_type', 'object_id') 

    def __str__(self):
        return f"بلاغ من {self.user.username} عن {self.content_object} - السبب: {self.get_reason_display()}"

