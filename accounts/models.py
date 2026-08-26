from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    PLACEHOLDER — Member 1 owns the real User model (auth, registration flow,
    any extra profile fields). This minimal version exists only so:
      1. AUTH_USER_MODEL can be set before the first migration (required —
         changing it later means resetting migrations across the whole project)
      2. assessments.Assessment.recruiter has something to ForeignKey against

    Member 1: extend this freely (add fields, override save, etc.) — just
    keep the model name "User" and the "role" field/values if other apps
    already depend on them by the time you get here.
    """
    ROLE_CHOICES = [
        ("recruiter", "Recruiter"),
        ("interviewee", "Interviewee"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="recruiter")
