from django.contrib.auth.models import User
from locksmith.hub.models import Key

class LocksmithBackend:
    """
    Authenticate with email address/key.

    * Try to log in with email+password
    * If no user exists try and create one with key as password
    """

    def authenticate(self, username=None, password=None):
        try:
            # if user exists with this email try and log in
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user

        except User.DoesNotExist:
            # if no user exists try and create one based on the key
            try:
                key = Key.objects.get(email=username)
                if key.key == password:
                    return User.objects.create_user(username[:30], username,
                                                    password)
            except Key.DoesNotExist:
                return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
