from django.urls import path
from . import views

# app_name lets you reference URLs as 'tracking:list', 'tracking:add', etc.
app_name = "tracking"

urlpatterns = [
    path("", views.tracking_list, name="list"),
    path("add/", views.tracking_add, name="add"),
    path("market/", views.market_search, name="market"),
    path("market/pricing/", views.card_pricing, name="card_pricing"),
    path("market/watch/", views.market_watch, name="market_watch"),
    path("market/compare/", views.market_compare, name="market_compare"),
    path("<int:pk>/", views.tracking_detail, name="detail"),
    path("<int:pk>/edit/", views.tracking_edit, name="edit"),
    path("<int:pk>/delete/", views.tracking_delete, name="delete"),
]
