from rest_framework.permissions import BasePermission


class IsAssessmentOwner(BasePermission):
    """
    Recruiters can access their own assessments.
    Interviewees can view published/open assessments.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Recruiter owns the assessment
        if user.role == "RECRUITER":
            return obj.recruiter_id == user.id

        # Interviewees can view published/open assessments
        if user.role == "INTERVIEWEE":
            return (
                request.method in ["GET", "HEAD", "OPTIONS"]
                and obj.status == "open"
            )

        return False


class IsQuestionOwner(BasePermission):
    """
    Only the recruiter who owns the assessment can manage questions.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == "RECRUITER"
            and obj.assessment.recruiter_id == request.user.id
        )


class IsChoiceOwner(BasePermission):
    """
    Only the recruiter who owns the assessment can manage choices.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == "RECRUITER"
            and obj.question.assessment.recruiter_id == request.user.id
        )
