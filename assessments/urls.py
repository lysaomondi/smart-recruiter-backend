"""
Assessment URLs
URL configuration for assessment and question endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, QuestionViewSet

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
]