from django.urls import path, include
from .views import history, index

urlpatterns = [
    path('', index, name='index'),
    path("scan/", include("scan.urls")),
]
