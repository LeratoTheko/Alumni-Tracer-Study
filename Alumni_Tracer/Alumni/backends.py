# backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class CustomBackend(ModelBackend):
    """
    Custom authentication backend for regular users.
    Implement authentication logic as needed.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Query the default user model to find the user with the provided username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # If the user doesn't exist, return None
            return None

        # Check if the provided password matches the user's password
        if user.check_password(password):
            # If the password matches, return the user object
            return user
        else:
            # If the password doesn't match, return None
            return None
