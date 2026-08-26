from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feedback, Result
from .permissions import IsInterviewee, IsRecruiter
from .serializers import (
    FeedbackSerializer,
    ResultDetailSerializer,
    ResultRankingSerializer,
    ResultSerializer,
    ResultStatisticsSerializer,
)
from .services import (
    get_result_rankings,
    get_result_statistics,
)


class ResultListView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsRecruiter,
    ]

    def get(self, request):
        results = (
            Result.objects
            .select_related("attempt")
            .order_by("-created_at")
        )

        serializer = ResultSerializer(
            results,
            many=True,
        )

        return Response(serializer.data)


class ResultRankingView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsRecruiter,
    ]

    def get(self, request):
        rankings = get_result_rankings()

        data = []

        for item in rankings:
            serializer = ResultRankingSerializer(
                item["result"],
                context={
                    "rank": item["rank"],
                },
            )

            data.append(serializer.data)

        return Response(data)


class ResultDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsRecruiter,
    ]

    def get(self, request, result_id):
        result = get_object_or_404(
            Result.objects.prefetch_related("feedback"),
            id=result_id,
        )

        serializer = ResultDetailSerializer(result)

        return Response(serializer.data)


class ReleaseResultView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsRecruiter,
    ]

    def post(self, request, result_id):
        result = get_object_or_404(
            Result,
            id=result_id,
        )

        if result.status == Result.STATUS_RELEASED:
            return Response(
                {
                    "message": "Result is already released.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result.status = Result.STATUS_RELEASED
        result.released_at = timezone.now()

        result.save(
            update_fields=[
                "status",
                "released_at",
                "updated_at",
            ]
        )

        return Response(
            ResultSerializer(result).data,
            status=status.HTTP_200_OK,
        )


class ResultStatisticsView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsRecruiter,
    ]

    def get(self, request):
        statistics = get_result_statistics()

        serializer = ResultStatisticsSerializer(
            statistics
        )

        return Response(serializer.data)


class MyResultsView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsInterviewee,
    ]

    def get(self, request):
        results = (
            Result.objects
            .filter(
                attempt__user=request.user,
                status=Result.STATUS_RELEASED,
            )
            .prefetch_related("feedback")
            .order_by("-created_at")
        )

        serializer = ResultDetailSerializer(
            results,
            many=True,
        )

        return Response(serializer.data)


class FeedbackListCreateView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsRecruiter,
    ]

    def get(self, request, result_id):
        result = get_object_or_404(
            Result,
            id=result_id,
        )

        feedback = (
            Feedback.objects
            .filter(result=result)
            .order_by("-created_at")
        )

        serializer = FeedbackSerializer(
            feedback,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request, result_id):
        result = get_object_or_404(
            Result,
            id=result_id,
        )

        serializer = FeedbackSerializer(
            data={
                **request.data,
                "result": result.id,
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        feedback = serializer.save(
            recruiter=request.user,
        )

        return Response(
            FeedbackSerializer(feedback).data,
            status=status.HTTP_201_CREATED,
        )


class FeedbackDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsRecruiter,
    ]

    def put(self, request, feedback_id):
        feedback = get_object_or_404(
            Feedback,
            id=feedback_id,
        )

        if feedback.recruiter != request.user:
            return Response(
                {
                    "message": (
                        "You are not authorized to "
                        "update this feedback."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = FeedbackSerializer(
            feedback,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        feedback = serializer.save()

        return Response(
            FeedbackSerializer(feedback).data
        )

    def delete(self, request, feedback_id):
        feedback = get_object_or_404(
            Feedback,
            id=feedback_id,
        )

        if feedback.recruiter != request.user:
            return Response(
                {
                    "message": (
                        "You are not authorized to "
                        "delete this feedback."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        feedback.delete()

        return Response(
            {
                "message": "Feedback deleted successfully."
            },
            status=status.HTTP_200_OK,
        )