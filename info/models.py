from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class Resource(models.Model):
    """
    النموذج الذي يمثّل موردًا واحدًا (مقال، رابط، ملف) ضمن قسم الموارد.
    """
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان المورد"
    )
    description = models.TextField(
        blank=True,
        verbose_name="الوصف"
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="رابط المورد"
    )
    file = models.FileField(
        upload_to='resources_files/',
        blank=True,
        null=True,
        verbose_name="الملف (PDF, DOCX, TXT، إلخ)",
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx']
        )]
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="تم الإنشاء بواسطة"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "مورد"
        verbose_name_plural = "الموارد"

    def __str__(self):
        return self.title

    def get_file_extension(self):
        """إرجاع امتداد الملف في حال تم رفعه."""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None

    def get_resource_type(self):
        """تحديد نوع المورد: رابط أو ملف أو كلاهما أو نص فقط."""
        if self.url and not self.file:
            return 'link'
        elif self.file and not self.url:
            return 'file'
        elif self.url and self.file:
            return 'both'
        return 'text_only'


class ContactMessage(models.Model):
    """
    نموذج يمثل رسالة تواصل بين المستخدم والطبيب النفسي (الأدمن).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contact_messages',
        verbose_name="المستخدم"
    )
    subject = models.CharField(
        max_length=200,
        verbose_name="الموضوع"
    )
    message = models.TextField(
        verbose_name="نص الرسالة"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإرسال"
    )

    reply = models.TextField(
        blank=True,
        verbose_name="الرد"
    )
    replied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الرد"
    )
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replied_messages',
        verbose_name="تم الرد بواسطة"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"

    def __str__(self):
        return f"{self.subject} - {self.user.username}"

    @property
    def is_replied(self):
        """يُرجع True إذا تم الرد على الرسالة."""
        return bool(self.reply and self.replied_at)
