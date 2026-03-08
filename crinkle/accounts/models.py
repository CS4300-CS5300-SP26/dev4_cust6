from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def get_initials(self):
        name = self.user.get_full_name()
        if name:
            parts = name.split()
            return (parts[0][0] + parts[-1][0]).upper()
        return self.user.username[:2].upper()

    def __str__(self):
        return f"{self.user.username}'s profile"