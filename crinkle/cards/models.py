from django.db import models
from django.contrib.auth.models import User


class GradeReport(models.Model):
    grade = models.TextField()


class Card(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400)
    date_scanned = models.DateField()
    grading_notes = models.OneToOneField(GradeReport, on_delete=models.CASCADE)

    picture_path = models.CharField(max_length=400)
    user_notes = models.TextField()


class CardCollection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cards = models.ForeignKey(Card, on_delete=models.CASCADE)
