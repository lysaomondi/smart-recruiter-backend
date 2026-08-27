"""Database models for assessment invitations."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class InvitationStatus(models.TextChoices):
    """States an invitation can move through during its lifetime."""
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
    EXPIRED = "expired", "Expired"


class Invitation(models.Model):
    """A recruiter's invitation for one candidate to take one assessment."""
    assessment = models.ForeignKey("assessments.Assessment", on_delete=models.CASCADE, related_name="invitations")
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations")
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invitations")
    status = models.CharField(max_length=20, choices=InvitationStatus.choices, default=InvitationStatus.PENDING)
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["assessment", "candidate"], name="unique_assessment_invitation")]

    def __str__(self):
        return f"{self.candidate} invited to {self.assessment}"

    @property
    def is_expired(self):
        """Return whether the optional invitation deadline has passed."""
        return bool(self.expires_at and timezone.now() >= self.expires_at)

    def refresh_status(self):
        """Persist an expired status when a deadline has elapsed."""
        if self.status == InvitationStatus.PENDING and self.is_expired:
            self.status = InvitationStatus.EXPIRED
            self.save(update_fields=["status", "updated_at"])
        return self.status
