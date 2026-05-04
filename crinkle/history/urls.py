from django.urls import path

# from .views import history
from cards.views import CardViewSet

urlpatterns = [
    # path('', history, name='history'),
    path("", CardViewSet.as_view({"get": "history"}), name="history"),
]
