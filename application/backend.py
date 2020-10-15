from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoseNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user