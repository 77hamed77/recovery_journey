# Generated by Django 5.2.3 on 2025-07-21 15:11

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('url', models.URLField(blank=True, max_length=500, null=True, verbose_name='URL Link')),
                ('file', models.FileField(blank=True, null=True, upload_to='resources_files/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx'])], verbose_name='File (PDF, DOCX, TXT, etc.)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
            ],
            options={
                'verbose_name': 'Resource',
                'verbose_name_plural': 'Resources',
                'ordering': ['-created_at'],
            },
        ),
    ]
