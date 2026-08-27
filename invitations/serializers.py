"""Serializers used by the invitation endpoints."""

from rest_framework import serializers

from accounts.models import UserRole
from assessments.models import AssessmentStatus
from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    """Read/write representation of an invitation."""
    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    candidate_name = serializers.SerializerMethodField()
    invited_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = ["id", "assessment", "assessment_title", "candidate", "candidate_name", "invited_by", "invited_by_name", "status", "expires_at", "accepted_at", "declined_at", "created_at", "updated_at"]
        read_only_fields = ["id", "invited_by", "status", "accepted_at", "declined_at", "created_at", "updated_at"]

    def get_candidate_name(self, invitation):
        return invitation.candidate.get_full_name() or invitation.candidate.username

    def get_invited_by_name(self, invitation):
        return invitation.invited_by.get_full_name() or invitation.invited_by.username

    def validate_assessment(self, assessment):
        if assessment.status != AssessmentStatus.PUBLISHED:
            raise serializers.ValidationError("Only published assessments can be invited.")
        return assessment

    def validate_candidate(self, candidate):
        if candidate.role != UserRole.CANDIDATE:
            raise serializers.ValidationError("Invitations can only be sent to candidates.")
        return candidate


class InvitationStatusSerializer(serializers.ModelSerializer):
    """Small response payload for accept and decline actions."""
    class Meta:
        model = Invitation
        fields = ["id", "status", "accepted_at", "declined_at", "expires_at"]
        read_only_fields = fields
