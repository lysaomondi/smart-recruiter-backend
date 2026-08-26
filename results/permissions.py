from rest_framework.permissions import BasePermission


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
            and getattr(user, "role", None) == "recruiter"
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
            and getattr(user, "role", None) == "interviewee"
        )