"""Endpoints used by candidates to manage assessment invitations."""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UserRole
from attempts.services import AttemptService
from .models import Invitation, InvitationStatus
from .serializers import InvitationSerializer, InvitationStatusSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    """List and create invitations; candidates can accept, decline, and start."""
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Invitation.objects.select_related("assessment", "candidate", "invited_by")
        if user.role == UserRole.RECRUITER:
            return Invitation.objects.filter(invited_by=user).select_related("assessment", "candidate", "invited_by")
        return Invitation.objects.filter(candidate=user).select_related("assessment", "candidate", "invited_by")

    def perform_create(self, serializer):
        """Only recruiters and admins may issue invitations."""
        if self.request.user.role not in (UserRole.ADMIN, UserRole.RECRUITER):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only recruiters and admins can create invitations.")
        serializer.save(invited_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="status")
    def status_summary(self, request):
        """Return candidate-facing invitations grouped by current status."""
        if request.user.role != UserRole.CANDIDATE:
            return Response({"detail": "This endpoint is for candidates."}, status=403)
        invitations = list(self.get_queryset())
        for invitation in invitations:
            invitation.refresh_status()
        return Response({state: InvitationSerializer([item for item in invitations if item.status == state], many=True).data for state in InvitationStatus.values})

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        invitation = self.get_object()
        if invitation.candidate != request.user:
            return Response({"detail": "Only the invited candidate can accept."}, status=403)
        invitation.refresh_status()
        if invitation.status != InvitationStatus.PENDING:
            return Response({"detail": "Only pending invitations can be accepted."}, status=400)
        invitation.status, invitation.accepted_at = InvitationStatus.ACCEPTED, timezone.now()
        invitation.save(update_fields=["status", "accepted_at", "updated_at"])
        return Response(InvitationStatusSerializer(invitation).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        invitation = self.get_object()
        if invitation.candidate != request.user:
            return Response({"detail": "Only the invited candidate can decline."}, status=403)
        invitation.refresh_status()
        if invitation.status != InvitationStatus.PENDING:
            return Response({"detail": "Only pending invitations can be declined."}, status=400)
        invitation.status, invitation.declined_at = InvitationStatus.DECLINED, timezone.now()
        invitation.save(update_fields=["status", "declined_at", "updated_at"])
        return Response(InvitationStatusSerializer(invitation).data)

    @action(detail=True, methods=["post"], url_path="attempt")
    def start_attempt(self, request, pk=None):
        """Create or return the candidate's in-progress attempt for an invitation."""
        invitation = self.get_object()
        if invitation.candidate != request.user:
            return Response({"detail": "Only the invited candidate can start this attempt."}, status=403)
        invitation.refresh_status()
        if invitation.status != InvitationStatus.ACCEPTED:
            return Response({"detail": "Accept the invitation before starting."}, status=400)
        attempt = AttemptService.start_attempt(invitation.assessment, request.user, invitation)
        return Response({"id": attempt.id, "status": attempt.status}, status=status.HTTP_201_CREATED)
