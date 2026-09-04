"""Candidate-facing attempt endpoints, including autosave and remaining time."""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UserRole
from assessments.models import Assessment
from .models import Answer, Attempt, AttemptStatus
from .serializers import (
    AnswerSerializer,
    AttemptDetailSerializer,
    AttemptListSerializer,
    AttemptSubmitSerializer,
)
from .services import AttemptService


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """Candidates see their attempts; recruiters see attempts for their assessments."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = Attempt.objects.select_related(
            "assessment",
            "candidate",
            "invitation",
        )

        if user.role == UserRole.ADMIN:
            return queryset

        if user.role == UserRole.RECRUITER:
            return queryset.filter(assessment__recruiter=user)

        return queryset.filter(candidate=user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AttemptDetailSerializer

        return AttemptListSerializer

    def _candidate_can_edit(self, attempt, request):
        return (
            attempt.candidate_id == request.user.id
            and attempt.status == AttemptStatus.IN_PROGRESS
        )

    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
        """Start or resume an assessment attempt for the authenticated candidate."""

        assessment_id = request.data.get("assessment_id")

        if not assessment_id:
            return Response(
                {"detail": "assessment_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            return Response(
                {"detail": "Assessment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if assessment.status != "open":
            return Response(
                {"detail": "This assessment is not currently open."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attempt = AttemptService.start_attempt(
            assessment=assessment,
            candidate=request.user,
        )

        return Response(
            AttemptDetailSerializer(
                attempt,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["put", "patch"], url_path="answers")
    def autosave_answer(self, request, pk=None):
        """Upsert one answer."""

        attempt = self.get_object()

        if not self._candidate_can_edit(attempt, request):
            return Response(
                {
                    "detail": (
                        "Only the candidate can edit an "
                        "in-progress attempt."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        question_id = request.data.get("question")

        if not question_id:
            return Response(
                {"detail": "question is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = Answer.objects.filter(
            attempt=attempt,
            question_id=question_id,
        ).first()

        serializer = AnswerSerializer(
            instance,
            data=request.data,
            partial=request.method == "PATCH",
            context={"attempt": attempt},
        )

        serializer.is_valid(raise_exception=True)

        answer = serializer.save(attempt=attempt)

        return Response(
            AnswerSerializer(
                answer,
                context={"attempt": attempt},
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="remaining-time")
    def remaining_time(self, request, pk=None):
        """Return the remaining assessment time."""

        attempt = self.get_object()

        if not attempt.start_time:
            return Response(
                {
                    "remaining_seconds": 0,
                    "expired": True,
                }
            )

        allowed_seconds = (
            attempt.assessment.time_limit_minutes * 60
        )

        elapsed_seconds = int(
            (timezone.now() - attempt.start_time).total_seconds()
        )

        remaining_seconds = max(
            allowed_seconds - elapsed_seconds,
            0,
        )

        return Response(
            {
                "remaining_seconds": remaining_seconds,
                "expired": remaining_seconds == 0,
            }
        )

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        """Grade and permanently submit the attempt."""

        attempt = self.get_object()

        if not self._candidate_can_edit(attempt, request):
            return Response(
                {
                    "detail": (
                        "Only the candidate can submit an "
                        "in-progress attempt."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AttemptSubmitSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        result = AttemptService.submit_attempt(attempt)

        return Response(
            {
                "message": "Attempt submitted successfully",
                "data": result,
            },
            status=status.HTTP_200_OK,
        )
