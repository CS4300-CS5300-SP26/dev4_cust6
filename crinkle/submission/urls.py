from django.urls import path
from . import views

app_name = "submission"
urlpatterns = [
    path("start/", views.submission_start, name="start"),
    path("details/", views.submission_details, name="details"),
    path("checkout/<int:pk>/", views.submission_checkout, name="checkout"),
    path("success/<int:pk>/", views.submission_success, name="success"),
    path("cancel/<int:pk>/", views.submission_cancel, name="cancel"),
    path(
        "confirmation/<int:pk>/",
        views.submission_confirmation,
        name="confirmation",
    ),
]
