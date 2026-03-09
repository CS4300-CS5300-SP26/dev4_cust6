from django.urls import path
from . import views

app_name = 'cards'
urlpatterns = [
    path('accounts/profile/collection/',
         views.collection_view,
         name='collection'
         ),
    path('accounts/profile/collection/save',
         views.save_report_view,
         name='save_report'
         ),
    path('scan/report/',
         views.scan_report_view,
         name='scan_report'
         ),
]
