from django.urls import path
from .views import education

urlpatterns = [
    path("", education, name="education"),
]
