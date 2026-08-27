"""
Attempt URLs
URL configuration for attempt endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttemptViewSet

router = DefaultRouter()
router.register(r'attempts', AttemptViewSet, basename='attempt')

urlpatterns = [
    path('', include(router.urls)),
]