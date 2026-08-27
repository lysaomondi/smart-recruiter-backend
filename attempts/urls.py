"""
Attempt URLs
URL configuration for attempt endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttemptViewSet

router = DefaultRouter()
# config.urls already mounts this app at /api/attempts/.
router.register(r'', AttemptViewSet, basename='attempt')

urlpatterns = [
    path('', include(router.urls)),
]
