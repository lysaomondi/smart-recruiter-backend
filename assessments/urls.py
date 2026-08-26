from django.urls import path
from .views import (
    AssessmentListCreateView,
    AssessmentDetailView,
    PublishAssessmentView,
    AddQuestionView,
)

urlpatterns = [
    path("assessments/", AssessmentListCreateView.as_view(), name="assessment-list-create"),
    path("assessments/<int:assessment_id>/", AssessmentDetailView.as_view(), name="assessment-detail"),
    path("assessments/<int:assessment_id>/publish/", PublishAssessmentView.as_view(), name="assessment-publish"),
    path("assessments/<int:assessment_id>/questions/", AddQuestionView.as_view(), name="assessment-add-question"),
]
