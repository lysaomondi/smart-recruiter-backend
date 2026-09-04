from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager for creating users with email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email address is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not password:
            raise ValueError("A password is required for a superuser.")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        RECRUITER = "RECRUITER", "Recruiter"
        INTERVIEWEE = "INTERVIEWEE", "Interviewee"

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    full_name = models.CharField(
        max_length=150,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "role"]

    def __str__(self):
        return self.email

class UserRole:
    """
    Compatibility shim — Member 3's attempts/invitations code imports
    UserRole.ADMIN/RECRUITER/CANDIDATE from accounts.models, but the real
    User model (above) uses User.Role.RECRUITER/INTERVIEWEE instead.
    This maps their expected names onto the real values so their code
    works unchanged. ADMIN has no real counterpart yet — it's a distinct
    value that simply won't match any current user until admin support
    is actually built.
    """
    ADMIN = "ADMIN"
    RECRUITER = User.Role.RECRUITER
    CANDIDATE = User.Role.INTERVIEWEE
