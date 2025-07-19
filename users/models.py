# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    THEME_CHOICES = (
        ('muslim', 'إسلامي'),
        ('universal', 'عالمي'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    content_preference = models.CharField(
        max_length=10, 
        choices=THEME_CHOICES, 
        default='muslim',  # <-- القيمة الافتراضية هي "مسلم"
        verbose_name="تفضيل المحتوى"
    )

    def __str__(self):
        return f"ملف {self.user.username}"

# هذه الإشارة (Signal) تقوم بإنشاء ملف شخصي تلقائياً لكل مستخدم جديد
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()