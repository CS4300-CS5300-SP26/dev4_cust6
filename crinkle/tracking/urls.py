from django.urls import path
from . import views

# app_name lets you reference URLs as 'tracking:list', 'tracking:add', etc.
app_name = 'tracking'

urlpatterns = [
    path('', views.tracking_list, name='list'),              # /tracking/
    path('add/', views.tracking_add, name='add'),             # /tracking/add/
    path('<int:pk>/', views.tracking_detail, name='detail'),  # /tracking/1/
    path('<int:pk>/edit/', views.tracking_edit, name='edit'),  # /tracking/1/edit/
    path('<int:pk>/delete/', views.tracking_delete, name='delete'),  # /tracking/1/delete/
]