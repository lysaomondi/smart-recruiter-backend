"""
Assessment Views
API views for assessments and questions.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Assessment, Question, Choice
from .serializers import (
    AssessmentListSerializer, AssessmentDetailSerializer,
    AssessmentCreateSerializer, QuestionSerializer,
    QuestionBulkCreateSerializer
)
from .permissions import IsAssessmentCreator, CanManageQuestions


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assessment CRUD operations.
    """
    permission_classes = [IsAuthenticated, IsAssessmentCreator]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'status']
    
    def get_queryset(self):
        """Get assessments based on user role"""
        user = self.request.user
        
        # Admin can see all assessments
        if user.role == 'ADMIN':
            return Assessment.objects.all()
        
        # Recruiter can see their own assessments
        if user.role == 'RECRUITER':
            return Assessment.objects.filter(created_by=user)
        
        # Candidate can see published assessments they have access to
        return Assessment.objects.filter(status='published')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return AssessmentCreateSerializer
        if self.action == 'retrieve':
            return AssessmentDetailSerializer
        if self.action == 'list':
            return AssessmentListSerializer
        return AssessmentListSerializer
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='questions/bulk')
    def bulk_create_questions(self, request, pk=None):
        """
        Bulk create questions for an assessment.
        """
        assessment = self.get_object()
        
        # Check permission
        if not CanManageQuestions().has_object_permission(request, self, assessment):
            return Response(
                {'error': 'You do not have permission to manage questions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = QuestionBulkCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        questions_data = serializer.validated_data['questions']
        created_questions = []
        
        for question_data in questions_data:
            # Set assessment and created_by
            question_data['assessment'] = assessment.id
            question_data['created_by'] = request.user.id
            
            question_serializer = QuestionSerializer(data=question_data)
            if question_serializer.is_valid():
                question = question_serializer.save()
                created_questions.append(question_serializer.data)
        
        return Response({
            'message': f'Created {len(created_questions)} questions',
            'questions': created_questions
        }, status=status.HTTP_201_CREATED)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Question CRUD operations.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, CanManageQuestions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assessment', 'question_type', 'difficulty']
    search_fields = ['question_text']
    ordering_fields = ['order_index', 'created_at', 'points']
    
    def get_queryset(self):
        """Get questions based on user role"""
        user = self.request.user
        
        # Admin can see all questions
        if user.role == 'ADMIN':
            return Question.objects.all()
        
        # Recruiter can see questions in their assessments
        if user.role == 'RECRUITER':
            return Question.objects.filter(assessment__created_by=user)
        
        # Candidate can see questions in published assessments
        return Question.objects.filter(assessment__status='published')
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_assessment(self, request):
        """Get questions for a specific assessment"""
        assessment_id = request.query_params.get('assessment_id')
        if not assessment_id:
            return Response(
                {'error': 'assessment_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assessment = get_object_or_404(Assessment, id=assessment_id)
        
        # Check access
        if not CanManageQuestions().has_object_permission(request, self, assessment):
            return Response(
                {'error': 'You do not have access to this assessment'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        questions = Question.objects.filter(assessment=assessment).order_by('order_index')
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)
