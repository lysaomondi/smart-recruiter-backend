from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Assessment, Question, Choice
from .serializers import (
    AssessmentSerializer,
    AssessmentCreateSerializer,
    AssessmentUpdateSerializer,
    QuestionSerializer,
)
from .permissions import IsAssessmentOwner


class AssessmentListCreateView(generics.ListCreateAPIView):
    """GET /api/assessments/  and  POST /api/assessments/"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(recruiter=self.request.user)

    def get_serializer_class(self):
        return AssessmentCreateSerializer if self.request.method == "POST" else AssessmentSerializer

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user, status="draft")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Re-serialize with the full read shape so the frontend gets questions/status back
        assessment = Assessment.objects.get(pk=response.data["id"] if "id" in response.data else None) \
            if "id" in response.data else None
        return response


class AssessmentDetailView(generics.RetrieveUpdateAPIView):
    """GET /api/assessments/:id/  and  PATCH /api/assessments/:id/"""
    permission_classes = [IsAuthenticated, IsAssessmentOwner]
    lookup_url_kwarg = "assessment_id"

    def get_queryset(self):
        return Assessment.objects.filter(recruiter=self.request.user)

    def get_serializer_class(self):
        return AssessmentUpdateSerializer if self.request.method == "PATCH" else AssessmentSerializer

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(AssessmentSerializer(instance).data)


class PublishAssessmentView(APIView):
    """POST /api/assessments/:id/publish/"""
    permission_classes = [IsAuthenticated, IsAssessmentOwner]

    def post(self, request, assessment_id):
        assessment = generics.get_object_or_404(Assessment, pk=assessment_id, recruiter=request.user)
        self.check_object_permissions(request, assessment)
        assessment.status = "open"
        assessment.save()
        return Response(AssessmentSerializer(assessment).data)


class AddQuestionView(APIView):
    """POST /api/assessments/:id/questions/"""
    permission_classes = [IsAuthenticated, IsAssessmentOwner]

    def post(self, request, assessment_id):
        assessment = generics.get_object_or_404(Assessment, pk=assessment_id, recruiter=request.user)
        self.check_object_permissions(request, assessment)

        serializer = QuestionSerializer(data=request.data, context={"assessment": assessment})
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
