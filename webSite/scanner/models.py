from django.db import models
from django.utils import timezone


class QRCode(models.Model):
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.data
