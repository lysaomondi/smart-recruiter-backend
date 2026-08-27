"""
Result Views
API views for result management.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Result
from .serializers import ResultSerializer, ResultListSerializer
from .services import ResultService
from accounts.permissions import IsAdminOrRecruiter


class ResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Result operations.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assessment', 'candidate', 'passed']
    search_fields = ['candidate__email', 'assessment__title']
    ordering_fields = ['created_at', 'percentage']
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'list':
            return ResultListSerializer
        return ResultSerializer
    
    def get_queryset(self):
        """Get results based on user role"""
        user = self.request.user
        
        # Admin can see all results
        if user.role == 'ADMIN':
            return Result.objects.all()
        
        # Recruiter can see results for their assessments
        if user.role == 'RECRUITER':
            return Result.objects.filter(assessment__created_by=user)
        
        # Candidate can see their own results
        return Result.objects.filter(candidate=user)
    
    @action(detail=False, methods=['get'], url_path='candidate/(?P<candidate_id>[^/.]+)')
    def get_candidate_results(self, request, candidate_id=None):
        """
        Get all results for a specific candidate.
        """
        user = request.user
        
        # Check permission
        if user.role not in ['ADMIN', 'RECRUITER'] and user.id != int(candidate_id):
            return Response(
                {'error': 'You do not have permission to view these results'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        results = Result.objects.filter(candidate_id=candidate_id)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='assessment/(?P<assessment_id>[^/.]+)/stats')
    def get_assessment_stats(self, request, assessment_id=None):
        """
        Get statistics for an assessment.
        """
        user = request.user
        
        # Check permission
        from assessments.models import Assessment
        assessment = Assessment.objects.get(id=assessment_id)
        
        if user.role not in ['ADMIN', 'RECRUITER']:
            return Response(
                {'error': 'You do not have permission to view these statistics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.role == 'RECRUITER' and assessment.created_by != user:
            return Response(
                {'error': 'You do not have permission to view this assessment\'s statistics'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = ResultService.get_assessment_statistics(assessment_id)
        return Response(stats)
    
    @action(detail=False, methods=['get'], url_path='my-stats')
    def get_my_stats(self, request):
        """
        Get statistics for the current user (candidate).
        """
        user = request.user
        
        if user.role != 'CANDIDATE':
            return Response(
                {'error': 'Only candidates can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = ResultService.get_candidate_statistics(user.id)
        return Response(stats)