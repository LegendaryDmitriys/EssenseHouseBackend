from django.contrib.auth.backends import ModelBackend
from .models import AdminUser

class AdminUserBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
