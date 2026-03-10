from django.db import models

# User Model
class User(models.Model):
    pass

class Card(models.Model):
    image = models.ImageField(upload_to='cards/')
    name = models.CharField(max_length=100, blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Unknown'} ({self.scanned_at.strftime('%Y-%m-%d %H:%M')})"

class GradeReport(models.Model):
    grade = models.TextField()