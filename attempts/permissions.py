"""
Attempt Permissions
Custom permissions for attempt views.
"""

from rest_framework import permissions

from accounts.models import User


class CanViewAttempt(permissions.BasePermission):
    """
    Permission to view attempts.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Recruiter can view attempts for their assessments
        if request.user.role == User.Role.RECRUITER:
            return obj.assessment.recruiter_id == request.user.id
        
        # Candidates can view their own attempts
        if request.user.role == User.Role.INTERVIEWEE:
            return obj.candidate_id == request.user.id
        
        return False


class CanManageAttempt(permissions.BasePermission):
    """
    Permission to manage (create/update) attempts.
    """
    
    def has_permission(self, request, view):
        # Only authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # Recruiters can manage attempts in their assessments
        if request.user.role == User.Role.RECRUITER:
            return obj.assessment.recruiter_id == request.user.id
        
        # Candidates can manage their own attempts
        if request.user.role == User.Role.INTERVIEWEE:
            return obj.candidate_id == request.user.id
        
        return False
