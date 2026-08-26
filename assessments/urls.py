from django.urls import path
from .views import (
    AssessmentListCreateView,
    AssessmentDetailView,
    PublishAssessmentView,
    CloseAssessmentView,
    QuestionListCreateView,
    QuestionDetailView,
    ChoiceListCreateView,
    ChoiceDetailView,
)

urlpatterns = [
    path("assessments/", AssessmentListCreateView.as_view(), name="assessment-list-create"),
    path("assessments/<int:assessment_id>/", AssessmentDetailView.as_view(), name="assessment-detail"),
    path("assessments/<int:assessment_id>/publish/", PublishAssessmentView.as_view(), name="assessment-publish"),
    path("assessments/<int:assessment_id>/close/", CloseAssessmentView.as_view(), name="assessment-close"),

    path(
        "assessments/<int:assessment_id>/questions/",
        QuestionListCreateView.as_view(), name="question-list-create"
    ),
    path(
        "assessments/<int:assessment_id>/questions/<int:question_id>/",
        QuestionDetailView.as_view(), name="question-detail"
    ),

    path(
        "assessments/<int:assessment_id>/questions/<int:question_id>/choices/",
        ChoiceListCreateView.as_view(), name="choice-list-create"
    ),
    path(
        "assessments/<int:assessment_id>/questions/<int:question_id>/choices/<int:choice_id>/",
        ChoiceDetailView.as_view(), name="choice-detail"
    ),
]
