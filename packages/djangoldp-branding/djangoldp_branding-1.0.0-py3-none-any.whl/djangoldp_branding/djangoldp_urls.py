from django.conf import settings
from django.urls import path
from . import views

if settings.DEBUG:
    urlpatterns = [
        path('templates-registry/', views.BrandingViewset),
        path('templates-registry/<parameters>/', views.BrandingViewset)
    ]
else:
    urlpatterns = []
