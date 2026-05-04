from django.db import models
from django.contrib.auth.models import User


class Submission(models.Model):
    SERVICE_CHOICES = [
        ("PSA", "PSA"),
        ("BGS", "BGS"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    card_name = models.CharField(max_length=400)
    grading_service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=200)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    stripe_session_id = models.CharField(
        max_length=200, blank=True, default=""
    )
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.card_name} to {self.grading_service}"
