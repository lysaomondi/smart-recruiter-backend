"""Serializers used by the invitation endpoints."""

from rest_framework import serializers

from accounts.models import UserRole
from assessments.models import Assessment, AssessmentStatus, Choice, Question
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
        return invitation.candidate.full_name or invitation.candidate.email

    def get_invited_by_name(self, invitation):
        return invitation.invited_by.full_name or invitation.invited_by.email

    def validate_assessment(self, assessment):
        if assessment.status != AssessmentStatus.OPEN:
            raise serializers.ValidationError("Only open assessments can be invited.")
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


class CandidateChoiceSerializer(serializers.ModelSerializer):
    """Choices shown to an interviewee; correctness is intentionally hidden."""

    class Meta:
        model = Choice
        fields = ["id", "text"]
        read_only_fields = fields


class CandidateQuestionSerializer(serializers.ModelSerializer):
    """Question data required to take an accepted invitation assessment."""

    choices = CandidateChoiceSerializer(many=True, read_only=True)
    kataBdd = serializers.CharField(source="kata_bdd", read_only=True, allow_null=True)
    kataPseudocode = serializers.CharField(source="kata_pseudocode", read_only=True, allow_null=True)
    kataDifficulty = serializers.CharField(source="kata_difficulty", read_only=True, allow_null=True)

    class Meta:
        model = Question
        fields = [
            "id", "type", "prompt", "source", "choices",
            "kataBdd", "kataPseudocode", "kataDifficulty",
        ]
        read_only_fields = fields


class CandidateAssessmentSerializer(serializers.ModelSerializer):
    """Candidate-safe assessment representation for an accepted invitation."""

    timeLimitMinutes = serializers.IntegerField(source="time_limit_minutes", read_only=True)
    closesAt = serializers.DateTimeField(source="closes_at", read_only=True, allow_null=True)
    questions = CandidateQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = ["id", "title", "status", "timeLimitMinutes", "closesAt", "questions"]
        read_only_fields = fields
