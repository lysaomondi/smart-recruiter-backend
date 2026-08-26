from rest_framework.permissions import BasePermission


class IsAuthenticatedUser(BasePermission):
    """
    Allow access only to authenticated users.
    """

    message = "Authentication is required to access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )


class IsRecruiter(BasePermission):
    """
    Allow access only to authenticated recruiters.
    """

    message = "Recruiter access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.RECRUITER
        )


class IsInterviewee(BasePermission):
    """
    Allow access only to authenticated interviewees.
    """

    message = "Interviewee access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.INTERVIEWEE
        )