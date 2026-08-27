from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'smart-recruiter-backend',
        'version': '1.0.0',
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("assessments.urls")),
    path("api/", include("attempts.urls")),
    path("api/", include("invitations.urls")),
    path("api/", include("results.urls")),
    path("api/", include("integrations.urls")),
    path("health/", health_check, name="health_check"),
]
