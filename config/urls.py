"""
Main URL Configuration
URL configuration for the entire project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/assessments/', include('assessments.urls')),
    path('api/attempts/', include('attempts.urls')),
    path('api/results/', include('results.urls')),
    path('api/invitations/', include('invitations.urls')),
    path('api/integrations/', include('integrations.urls')),
]

# Include health check endpoint
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'smart-recruiter-backend',
        'version': '1.0.0'
    })

urlpatterns += [
    path('health/', health_check, name='health_check'),
]