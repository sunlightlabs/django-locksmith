from django.apps import apps

class LocksmithAuthConfig(apps.AuthConfig):
    label = 'locksmith_auth'
