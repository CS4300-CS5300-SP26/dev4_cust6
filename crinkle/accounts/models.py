from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def get_initials(self):
        first = self.user.first_name
        last = self.user.last_name
        if first and last:
            return (first[0] + last[0]).upper()
        return self.user.username[:2].upper()

    def __str__(self):
        return f"{self.user.username}'s profile"