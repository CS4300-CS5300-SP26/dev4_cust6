from django.urls import path
from .views import scan_page

urlpatterns = [
    path("", scan_page, name="scan"),
]

