from rest_framework.permissions import BasePermission


class IsAssessmentOwner(BasePermission):
    """Object is an Assessment — only its recruiter can view/edit/publish/close/delete it."""

    def has_object_permission(self, request, view, obj):
        return obj.recruiter_id == request.user.id


class IsQuestionOwner(BasePermission):
    """Object is a Question — ownership traces through question.assessment.recruiter."""

    def has_object_permission(self, request, view, obj):
        return obj.assessment.recruiter_id == request.user.id


class IsChoiceOwner(BasePermission):
    """Object is a Choice — ownership traces through choice.question.assessment.recruiter."""

    def has_object_permission(self, request, view, obj):
        return obj.question.assessment.recruiter_id == request.user.id
