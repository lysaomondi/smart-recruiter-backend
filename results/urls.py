from django.urls import path

from .views import (
    FeedbackDetailView,
    FeedbackListCreateView,
    MyResultsView,
    ReleaseResultView,
    ResultDetailView,
    ResultListView,
    ResultStatisticsView,
)


urlpatterns = [
    path(
        "results/",
        ResultListView.as_view(),
        name="result-list",
    ),

    path(
        "results/my/",
        MyResultsView.as_view(),
        name="my-results",
    ),

    path(
        "results/<int:result_id>/",
        ResultDetailView.as_view(),
        name="result-detail",
    ),

    path(
        "results/<int:result_id>/release/",
        ReleaseResultView.as_view(),
        name="result-release",
    ),

    path(
        "results/<int:result_id>/feedback/",
        FeedbackListCreateView.as_view(),
        name="feedback-list-create",
    ),

    path(
        "feedback/<int:feedback_id>/",
        FeedbackDetailView.as_view(),
        name="feedback-detail",
    ),

    path(
        "statistics/results/",
        ResultStatisticsView.as_view(),
        name="result-statistics",
    ),
]