from django.db import models
from django.contrib.auth.models import User


class GradeReport(models.Model):
    grade = models.TextField()


class Card(models.Model):
    name = models.CharField(max_length=400)
    date_scanned = models.DateField(auto_now=True)
    grading_notes = models.OneToOneField(GradeReport, on_delete=models.CASCADE)

    picture_path = models.CharField(max_length=400)
    user_notes = models.TextField()


class CardCollection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cards = models.ManyToManyField(Card)

    def __str__(self):
        return f'Collection of {self.user.username}'
