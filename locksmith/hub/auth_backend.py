from django.contrib.auth.models import User
from locksmith.hub.models import Key

class LocksmithBackend:
    """
    Authenticate with email address/key.
    """

    def authenticate(self, username=None, password=None):
        # figure out if authenticate works
        try:
            key = Key.objects.get(email=username)

            if key.key == password:
                user, created = User.objects.get_or_create(email=username,
                                   defaults={'username':username[:30]})
                if created:
                    user.set_password(password)
                    return user
            else:
                try:
                    user = User.objects.get(email=username)
                    if user.check_password(password):
                        return user
                except User.DoesNotExist:
                    return None
        except Key.DoesNotExist:
            return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
