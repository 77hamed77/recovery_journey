# info/models.py

from django.db import models
from django.conf import settings # <-- إضافة هذا الاستيراد
from django.core.validators import FileExtensionValidator

class Resource(models.Model):
    """
    Model representing a single resource (article, link, file) for the resources section.
    """
    # Resource title
    title = models.CharField(max_length=255, verbose_name="Title")
    
    # Resource description
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Optional URL for external resources
    url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL Link")
    
    # Optional file upload for internal resources
    file = models.FileField(
        upload_to='resources_files/',
        blank=True,
        null=True,
        verbose_name="File (PDF, DOCX, TXT, etc.)",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx'])]
    )
    
    # Date when the resource was created
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    
    # User who created/uploaded the resource (optional, can be admin)
    # استخدام settings.AUTH_USER_MODEL بدلاً من User
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Created By")

    class Meta:
        # Default ordering for resources: newest first
        ordering = ['-created_at']
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

    def __str__(self):
        """String representation of the Resource model."""
        return self.title

    def get_file_extension(self):
        """Returns the file extension if a file is uploaded."""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None

    def get_resource_type(self):
        """Determines if the resource is a link or a file."""
        if self.url and not self.file:
            return 'link'
        elif self.file and not self.url:
            return 'file'
        elif self.url and self.file:
            return 'both' # Or decide which one takes precedence
        return 'text_only' # If neither URL nor file, it's just text

