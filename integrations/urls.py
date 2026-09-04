from django.urls import path

from .views import (
    CodewarsCachedKataListView,
    CodewarsKataDetailView,
    CodewarsSearchView,
)


urlpatterns = [
    path(
        "codewars/search/",
        CodewarsSearchView.as_view(),
        name="codewars-search",
    ),
    path(
        "codewars/katas/",
        CodewarsCachedKataListView.as_view(),
        name="codewars-kata-list",
    ),
    path(
        "codewars/katas/<str:kata_id>/",
        CodewarsKataDetailView.as_view(),
        name="codewars-kata-detail",
    ),
]