"""
Account Models
Custom user model with role-based access.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """User role choices"""
    ADMIN = 'ADMIN', 'Admin'
    RECRUITER = 'RECRUITER', 'Recruiter'
    CANDIDATE = 'CANDIDATE', 'Candidate'


class User(AbstractUser):
    """
    Custom User model with role-based access.
    """
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CANDIDATE
    )
    company = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role,
            'company': self.company,
            'phone': self.phone,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }