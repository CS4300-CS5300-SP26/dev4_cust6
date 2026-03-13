from django.urls import path
from . import views

app_name = 'cards'
urlpatterns = [
    path('accounts/profile/collection/',
         views.CardCollectionViewSet.as_view({'get': 'retrieve'}),
         name='collection'
         ),
    path('accounts/profile/collection/<int:pk>/',
         views.CardViewSet.as_view({'get': 'retrieve'}),
         name='view_card'
         ),
    path('accounts/profile/collection/<int:pk>/save',
         views.CardViewSet.as_view({'post': 'update'}),
         name='save_card'
         ),
    path('scan/report/',
         views.scan_report_view,
         name='scan_report'
         ),
    path('accounts/profile/collection/save',
         views.save_report_view,
         name='save_report'
         ),
]
