"""
Attempt Permissions
Custom permissions for attempt views.
"""

from rest_framework import permissions


class CanViewAttempt(permissions.BasePermission):
    """
    Permission to view attempts.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can view all attempts
        if request.user.role == 'ADMIN':
            return True
        
        # Recruiter can view attempts for their assessments
        if request.user.role == 'RECRUITER':
            return obj.assessment.created_by == request.user
        
        # Candidates can view their own attempts
        if request.user.role == 'CANDIDATE':
            return obj.candidate == request.user
        
        return False


class CanManageAttempt(permissions.BasePermission):
    """
    Permission to manage (create/update) attempts.
    """
    
    def has_permission(self, request, view):
        # Only authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin can manage all attempts
        if request.user.role == 'ADMIN':
            return True
        
        # Recruiters can manage attempts in their assessments
        if request.user.role == 'RECRUITER':
            return obj.assessment.created_by == request.user
        
        # Candidates can manage their own attempts
        if request.user.role == 'CANDIDATE':
            return obj.candidate == request.user
        
        return False