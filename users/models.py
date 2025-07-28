# users/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class CustomUserManager(BaseUserManager):
    """
    مدير مخصص لنموذج المستخدم CustomUser.
    """
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('يجب تحديد اسم المستخدم')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # يجب أن يكون السوبر يوزر نشطاً افتراضياً

        if extra_fields.get('is_staff') is not True:
            raise ValueError('يجب أن يكون المستخدم المميز لديه is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('يجب أن يكون المستخدم المميز لديه is_superuser=True.')
        
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    نموذج مستخدم مخصص.
    يستخدم اسم المستخدم كحقل فريد للمصادقة.
    """
    username = models.CharField(max_length=150, unique=True, verbose_name="اسم المستخدم")
    is_staff = models.BooleanField(default=False, verbose_name="موظف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الانضمام")
    # تعيين تاريخ اليوم كقيمة افتراضية لـ start_date عند إنشاء المستخدم
    start_date = models.DateField(default=timezone.now, verbose_name="تاريخ البدء") # <-- تم التعديل هنا

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [] # لا توجد حقول مطلوبة أخرى غير USERNAME_FIELD وكلمة المرور

    class Meta:
        verbose_name = "المستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

# نموذج الملف الشخصي (Profile)
class Profile(models.Model):
    """
    نموذج الملف الشخصي للمستخدم لتخزين التفضيلات الإضافية.
    """
    THEME_CHOICES = (
        ('muslim', 'إسلامي'),
        ('universal', 'عالمي'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name="المستخدم")
    content_preference = models.CharField(
        max_length=10, 
        choices=THEME_CHOICES, 
        default='muslim', 
        verbose_name="تفضيل المحتوى"
    )
    is_verified = models.BooleanField(default=False, verbose_name="موثق / معتمد") # هذا الحقل موجود في النسخة التي زودتها لك في رد سابق

    class Meta:
        verbose_name = "الملف الشخصي"
        verbose_name_plural = "الملفات الشخصية"

    def __str__(self):
        return f"ملف {self.user.username}"

# إشارات لإنشاء وحفظ ملف Profile تلقائياً عند إنشاء/حفظ CustomUser
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    تنشئ ملف Profile جديد للمستخدم عند إنشاء CustomUser.
    """
    if created:
        Profile.objects.create(user=instance)
        # تمت إزالة هذا الجزء لأن start_date أصبح له default في النموذج
        # if not instance.start_date: 
        #     instance.start_date = timezone.localdate()
        #     instance.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    تحفظ ملف Profile الخاص بالمستخدم عند حفظ CustomUser.
    """
    instance.profile.save()