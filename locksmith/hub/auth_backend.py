from django.contrib.auth.models import User
from locksmith.hub.models import Key

class LocksmithBackend:
    """
    Authenticate with email address/key.
    """

    def authenticate(self, username=None, password=None):
        try:
            key = Key.objects.get(email=username, key=password)
            user, created = User.objects.get_or_create(username=username,
                                                       defaults={'email':username})
            if created:
                user.set_password(password)
                return user

            if user.check_password(password):
                return user
            else:
                return None
        except Key.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
