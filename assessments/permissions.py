from rest_framework.permissions import BasePermission


class IsAssessmentOwner(BasePermission):
    """Only the recruiter who created an assessment can view/edit/publish it."""

    def has_object_permission(self, request, view, obj):
        return obj.recruiter_id == request.user.id
