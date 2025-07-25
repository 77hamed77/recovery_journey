# Generated by Django 5.2.3 on 2025-07-23 18:42

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resource',
            options={'ordering': ['-created_at'], 'verbose_name': 'مورد', 'verbose_name_plural': 'الموارد'},
        ),
        migrations.AlterField(
            model_name='resource',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='تم الإنشاء بواسطة'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='description',
            field=models.TextField(blank=True, verbose_name='الوصف'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='resources_files/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx'])], verbose_name='الملف (PDF, DOCX, TXT، إلخ)'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='title',
            field=models.CharField(max_length=255, verbose_name='عنوان المورد'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='url',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='رابط المورد'),
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200, verbose_name='الموضوع')),
                ('message', models.TextField(verbose_name='نص الرسالة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')),
                ('reply', models.TextField(blank=True, verbose_name='الرد')),
                ('replied_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الرد')),
                ('replied_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replied_messages', to=settings.AUTH_USER_MODEL, verbose_name='تم الرد بواسطة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_messages', to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'رسالة تواصل',
                'verbose_name_plural': 'رسائل التواصل',
                'ordering': ['-created_at'],
            },
        ),
    ]
