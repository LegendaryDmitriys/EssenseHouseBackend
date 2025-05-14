from django.db import models

from django.db import models

class PushSubscription(models.Model):
    endpoint = models.TextField()
    keys = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
