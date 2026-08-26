from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assessments.urls')),
    # Other apps' urls.py are still empty — add as each member builds theirs:
    # path('api/', include('accounts.urls')),
    # path('api/', include('attempts.urls')),
    # path('api/', include('invitations.urls')),
    # path('api/', include('results.urls')),
]
