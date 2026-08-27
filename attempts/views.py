"""
Attempt Views
API views for attempt management.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Attempt, AttemptStatus
from .serializers import (
    AttemptListSerializer, AttemptDetailSerializer,
    AttemptCreateSerializer, AttemptSubmitSerializer,
    AttemptUpdateSerializer
)
from .permissions import CanViewAttempt, CanManageAttempt
from .services import AttemptService


class AttemptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attempt CRUD operations.
    """
    permission_classes = [IsAuthenticated, CanViewAttempt]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assessment', 'candidate', 'status']
    search_fields = ['assessment__title', 'candidate__email']
    ordering_fields = ['created_at', 'start_time', 'percentage']
    
    def get_queryset(self):
        """Get attempts based on user role"""
        user = self.request.user
        
        # Admin can see all attempts
        if user.role == 'ADMIN':
            return Attempt.objects.all()
        
        # Recruiter can see attempts in their assessments
        if user.role == 'RECRUITER':
            return Attempt.objects.filter(assessment__created_by=user)
        
        # Candidate can see their own attempts
        return Attempt.objects.filter(candidate=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return AttemptCreateSerializer
        if self.action == 'retrieve':
            return AttemptDetailSerializer
        if self.action == 'list':
            return AttemptListSerializer
        if self.action == 'update' or self.action == 'partial_update':
            return AttemptUpdateSerializer
        return AttemptListSerializer
    
    def perform_create(self, serializer):
        """Create attempt with service"""
        attempt = AttemptService.start_attempt(
            serializer.validated_data['assessment'],
            serializer.validated_data['candidate'],
            serializer.validated_data.get('invitation')
        )
        serializer.instance = attempt
    
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        Submit an attempt for grading.
        """
        attempt = self.get_object()
        
        # Check permission
        if not CanManageAttempt().has_object_permission(request, self, attempt):
            return Response(
                {'error': 'You do not have permission to submit this attempt'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if attempt can be submitted
        if not attempt.can_be_submitted():
            return Response(
                {'error': 'This attempt cannot be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Submit attempt
        result = AttemptService.submit_attempt(
            attempt,
            serializer.validated_data['answers']
        )
        
        return Response({
            'message': 'Attempt submitted successfully',
            'data': result
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='candidate/(?P<candidate_id>[^/.]+)')
    def get_candidate_attempts(self, request, candidate_id=None):
        """
        Get all attempts for a specific candidate.
        """
        user = request.user
        
        # Check permission
        if user.role not in ['ADMIN', 'RECRUITER'] and user.id != int(candidate_id):
            return Response(
                {'error': 'You do not have permission to view these attempts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        attempts = Attempt.objects.filter(candidate_id=candidate_id)
        serializer = self.get_serializer(attempts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='status/(?P<status>[^/.]+)')
    def get_by_status(self, request, status=None):
        """
        Get attempts by status.
        """
        if status not in AttemptStatus.values:
            return Response(
                {'error': f'Invalid status. Valid options: {AttemptStatus.values}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(status=status)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)