from django.db import models

from EssenseHouse import settings


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    endpoint = models.TextField()
    session_key = models.CharField(max_length=40, null=True, blank=True)
    keys = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
