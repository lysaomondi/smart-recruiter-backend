from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assessments.urls')),

    # TEMPORARY — Member 1 should move these into accounts/urls.py and build
    # proper register/login/me endpoints around them. Paths should stay the
    # same (/api/token/, /api/token/refresh/) so nothing else needs to change.
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
