"""Invitation URL routes."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InvitationViewSet

router = DefaultRouter()
# config.urls already mounts this app at /api/invitations/.
router.register(r'', InvitationViewSet, basename='invitation')

urlpatterns = [path('', include(router.urls))]
