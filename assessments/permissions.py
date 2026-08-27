"""
Assessment Permissions
Custom permissions for assessment and question views.
"""

from rest_framework import permissions


class IsAssessmentCreator(permissions.BasePermission):
    """
    Custom permission to only allow assessment creators to edit.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the creator
        return obj.created_by == request.user


class CanManageQuestions(permissions.BasePermission):
    """
    Permission to manage questions in an assessment.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin or recruiter can manage questions
        return request.user.role in ['ADMIN', 'RECRUITER']
    
    def has_object_permission(self, request, view, obj):
        # Admin can manage all questions
        if request.user.role == 'ADMIN':
            return True
        
        # Recruiter can manage questions in their assessments
        if request.user.role == 'RECRUITER':
            # Check if question belongs to an assessment created by this user
            if hasattr(obj, 'assessment'):
                return obj.assessment.created_by == request.user
            # Check if assessment is created by this user
            if hasattr(obj, 'created_by'):
                return obj.created_by == request.user
        
        return False