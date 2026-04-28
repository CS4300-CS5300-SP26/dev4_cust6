# NOTE: IMPLEMENTATION CHANGED TO USE MODELS DEFINED IN THE CARDS APP 

# from django.db import models

# User Model
# class User(models.Model):
#     pass

# class Card(models.Model):
#     image = models.ImageField(upload_to='cards/', blank=True, null=True)
#     name = models.CharField(max_length=100, blank=True)
#     grade = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
#     set_name = models.CharField(max_length=100, blank=True, default='Unknown Set')
#     date_scanned = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name or 'Unknown'} ({self.date_scanned})"
        
# class GradeReport(models.Model):
#     grade = models.TextField()