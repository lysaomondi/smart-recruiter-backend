from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

from .models import Assessment, AssessmentStatus, Question, Choice
from .serializers import (
    AssessmentSerializer,
    AssessmentCreateSerializer,
    AssessmentUpdateSerializer,
    QuestionSerializer,
    QuestionUpdateSerializer,
    ChoiceSerializer,
    ChoiceUpdateSerializer,
)
from .permissions import IsAssessmentOwner, IsQuestionOwner, IsChoiceOwner


# ---------------------------------------------------------------- Assessments

class AssessmentListCreateView(generics.ListCreateAPIView):
    """GET /api/assessments/  and  POST /api/assessments/"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(recruiter=self.request.user)

    def get_serializer_class(self):
        return AssessmentCreateSerializer if self.request.method == "POST" else AssessmentSerializer

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user, status=AssessmentStatus.DRAFT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Re-serialize with the full read shape (includes id/status/questions)
        full = AssessmentSerializer(serializer.instance)
        return Response(full.data, status=status.HTTP_201_CREATED)


class AssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/assessments/:id/  — also serves as the preview/detail endpoint
    PATCH  /api/assessments/:id/
    DELETE /api/assessments/:id/
    """
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
    """POST /api/assessments/:id/publish/ — draft -> open"""
    permission_classes = [IsAuthenticated, IsAssessmentOwner]

    def post(self, request, assessment_id):
        assessment = get_object_or_404(Assessment, pk=assessment_id, recruiter=request.user)
        self.check_object_permissions(request, assessment)
        assessment.status = AssessmentStatus.OPEN
        assessment.save()
        return Response(AssessmentSerializer(assessment).data)


class CloseAssessmentView(APIView):
    """POST /api/assessments/:id/close/ — open -> closed"""
    permission_classes = [IsAuthenticated, IsAssessmentOwner]

    def post(self, request, assessment_id):
        assessment = get_object_or_404(Assessment, pk=assessment_id, recruiter=request.user)
        self.check_object_permissions(request, assessment)
        assessment.status = AssessmentStatus.CLOSED
        assessment.save()
        return Response(AssessmentSerializer(assessment).data)


# ------------------------------------------------------------------ Questions

class QuestionListCreateView(generics.ListCreateAPIView):
    """GET /api/assessments/:aid/questions/  and  POST .../questions/"""
    permission_classes = [IsAuthenticated, IsAssessmentOwner]

    def get_assessment(self):
        assessment = get_object_or_404(Assessment, pk=self.kwargs["assessment_id"])
        self.check_object_permissions(self.request, assessment)
        return assessment

    def get_queryset(self):
        return self.get_assessment().questions.all()

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "assessment": self.get_assessment()}

    def get_serializer_class(self):
        return QuestionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/assessments/:aid/questions/:qid/"""
    permission_classes = [IsAuthenticated, IsQuestionOwner]
    lookup_url_kwarg = "question_id"

    def get_queryset(self):
        return Question.objects.filter(assessment_id=self.kwargs["assessment_id"])

    def get_serializer_class(self):
        return QuestionUpdateSerializer if self.request.method == "PATCH" else QuestionSerializer

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(QuestionSerializer(instance).data)


# -------------------------------------------------------------------- Choices

class ChoiceListCreateView(generics.ListCreateAPIView):
    """GET /api/assessments/:aid/questions/:qid/choices/  and  POST .../choices/"""
    permission_classes = [IsAuthenticated, IsQuestionOwner]
    serializer_class = ChoiceSerializer

    def get_question(self):
        question = get_object_or_404(
            Question, pk=self.kwargs["question_id"], assessment_id=self.kwargs["assessment_id"]
        )
        self.check_object_permissions(self.request, question)
        return question

    def get_queryset(self):
        return self.get_question().choices.all()

    def perform_create(self, serializer):
        question = self.get_question()
        order = question.choices.count()
        serializer.save(question=question, order=order)


class ChoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/assessments/:aid/questions/:qid/choices/:cid/"""
    permission_classes = [IsAuthenticated, IsChoiceOwner]
    lookup_url_kwarg = "choice_id"

    def get_queryset(self):
        return Choice.objects.filter(
            question_id=self.kwargs["question_id"],
            question__assessment_id=self.kwargs["assessment_id"],
        )

    def get_serializer_class(self):
        return ChoiceUpdateSerializer if self.request.method == "PATCH" else ChoiceSerializer

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(ChoiceSerializer(instance).data)
