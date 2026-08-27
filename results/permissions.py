from rest_framework.permissions import BasePermission

from accounts.models import User


class IsRecruiter(BasePermission):
    """
    Allows access only to authenticated recruiter users.
    """

    message = "Recruiter access required."

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.RECRUITER
        )


class IsInterviewee(BasePermission):
    """
    Allows access only to authenticated interviewee users.
    """

    message = "Interviewee access required."

    def has_permission(self, request, view):
        user = request.user

        return (
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.INTERVIEWEE
        )
