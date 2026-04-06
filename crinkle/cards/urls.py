from django.urls import path
from . import views

app_name = "cards"
urlpatterns = [
    path(
        "collection/",
        views.CardCollectionViewSet.as_view({"get": "retrieve"}),
        name="collection",
    ),
    path(
        "collection/<int:pk>/",
        views.CardViewSet.as_view({"get": "retrieve"}),
        name="view_card",
    ),
    path(
        "collection/<int:pk>/save",
        views.CardViewSet.as_view({"post": "update"}),
        name="save_card",
    ),
    path(
        "collection/<int:pk>/delete",
        views.delete_card_view,
        name="delete_card",
    ),
    path("scan/report/", views.scan_report_view, name="scan_report"),
    path("collection/save", views.save_report_view, name="save_report"),
    path(
        "collection/settings",
        views.CardCollectionViewSet.as_view(
            {
                "get": "collection_settings",
                "post": "collection_settings",
            }
        ),
        name="collection_settings",
    ),
]