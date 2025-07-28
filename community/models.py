# community/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.functions import Lower
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
import markdown2 # <-- إضافة هذا الاستيراد

class Post(models.Model):
    """
    نموذج يمثل منشورًا في المجتمع.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts', verbose_name="المستخدم")
    title = models.CharField(max_length=200, verbose_name="عنوان المنشور")
    content = models.TextField(verbose_name="محتوى المنشور")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ آخر تعديل")

    # تعريف GenericRelation لجلب الإعجابات المرتبطة بهذا المنشور
    likes_relation = GenericRelation('community.Like')
    
    class Meta:
        verbose_name = "منشور المجتمع"
        verbose_name_plural = "منشورات المجتمع"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('community:post_detail', args=[str(self.id)])
    
    @property
    def get_likes_count(self):
        return self.likes_relation.count()
    
    @property
    def rendered_content(self): # <-- إضافة خاصية معالجة Markdown
        return markdown2.markdown(self.content, extras=["fenced-code-blocks", "tables", "footnotes"])

class Comment(models.Model):
    """
    نموذج يمثل تعليقًا على منشور معين، مع دعم الردود المتداخلة.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="المنشور")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comments', verbose_name="المستخدم")
    content = models.TextField(verbose_name="محتوى التعليق")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="تعليق أم")

    # تعريف GenericRelation لجلب الإعجابات المرتبطة بهذا التعليق
    likes_relation = GenericRelation('community.Like')

    class Meta:
        verbose_name = "تعليق المجتمع"
        verbose_name_plural = "تعليقات المجتمع"
        ordering = ['created_at']

    def __str__(self):
        return f"تعليق من {self.user.username} على {self.post.title[:50]}..."
    
    @property
    def get_likes_count(self):
        return self.likes_relation.count()
    
    @property
    def rendered_content(self): # <-- إضافة خاصية معالجة Markdown
        return markdown2.markdown(self.content, extras=["fenced-code-blocks", "tables", "footnotes"])


class Like(models.Model):
    """
    نموذج يمثل إعجابًا بمنشور أو تعليق.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes', verbose_name="المستخدم")
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) 
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id') 
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإعجاب")

    class Meta:
        verbose_name = "إعجاب"
        verbose_name_plural = "إعجابات"
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} أعجب بـ {self.content_object}"

class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following', verbose_name="المتابع")
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers', verbose_name="المتبوع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المتابعة")

    class Meta:
        verbose_name = "متابعة"
        verbose_name_plural = "متابعات"
        unique_together = ('user', 'followed_user') # لا يمكن للمستخدم متابعة نفس الشخص مرتين
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} يتابع {self.followed_user.username}"


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
        usernames = ", ".join([user.username for user in self.participants.all()])
        return f"محادثة بين {usernames}"

class Message(models.Model):
    """
    نموذج يمثل رسالة واحدة داخل محادثة.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name="المحادثة")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="المرسل")
    content = models.TextField(verbose_name="محتوى الرسالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    is_read = models.BooleanField(default=False, verbose_name="تمت القراءة")

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "رسائل" # تم تصحيح verbose_plural
        ordering = ['created_at'] # ترتيب الرسائل من الأقدم إلى الأحدث

    def __str__(self):
        return f"رسالة من {self.sender.username} في {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Report(models.Model):
    """
    نموذج يمثل بلاغاً عن محتوى (منشور أو تعليق).
    """
    REASON_CHOICES = (
        ('spam', 'محتوى غير مرغوب فيه/سبام'),
        ('hate_speech', 'خطاب كراهية/عنصري'),
        ('harassment', 'مضايقة/تنمر'),
        ('inappropriate', 'محتوى غير لائق/غير مناسب'),
        ('self_harm', 'إيذاء الذات/الانتحار'),
        ('drug_related', 'ترويج مواد إدمانية'),
        ('other', 'أخرى'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_reports', verbose_name="المبلغ")
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, verbose_name="السبب")
    description = models.TextField(blank=True, null=True, verbose_name="وصف إضافي")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ البلاغ")
    is_resolved = models.BooleanField(default=False, verbose_name="تم الحل")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) 
    object_id = models.PositiveIntegerField()
    reported_object = GenericForeignKey('content_type', 'object_id') 

    class Meta:
        verbose_name = "بلاغ محتوى"
        verbose_name_plural = "بلاغات المحتوى"
        ordering = ['-created_at']

    def __str__(self):
        return f"بلاغ من {self.user.username} عن {self.reported_object_type} - {self.reason}"
    
    @property
    def reported_object_type(self):
        """يعيد نوع الكائن المبلغ عنه (مثال: 'Post' أو 'Comment')."""
        return self.content_type.model.capitalize() # تحويل 'post' إلى 'Post' وهكذا
