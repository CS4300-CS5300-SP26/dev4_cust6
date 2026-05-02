from django.urls import path
from . import views

app_name = "submission"

urlpatterns = [
    path("start/", views.submission_start, name="start"),
    path("details/", views.submission_details, name="details"),
    path("confirmation/<int:pk>/", views.submission_confirmation, name="confirmation"),
]
