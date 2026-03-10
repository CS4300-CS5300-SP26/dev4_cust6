from django.urls import path
from .views import index, history

urlpatterns = [
    path('', index, name='index'),
    path('history/', history, name='history'),
]
