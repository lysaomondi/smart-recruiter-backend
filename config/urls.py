from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

    # Results API
    path("api/", include("results.urls")),

    # Codewars integration API
    path("api/", include("integrations.urls")),
]