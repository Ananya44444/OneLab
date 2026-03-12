from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default="processed")

    def __str__(self):
        return f"{self.title} ({self.status})"
