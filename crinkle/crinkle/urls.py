"""
URL configuration for Crinkle.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from home.views import index

urlpatterns = [
    path('', index, name='index'),
    path('', include('home.urls')),
    path('history/', include('history.urls')),
    path('tracking/', include('tracking.urls')),
    path('accounts/', include('accounts.urls')),
    path('cards/', include('cards.urls')),
    path('scan/', include('scan.urls')),
    path('submission/', include('submission.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
