from django.utils import timezone
from django.db import models

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    size = models.BigIntegerField()
    file_type = models.CharField(max_length=50)