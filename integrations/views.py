from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CodewarsKata
from .serializers import CodewarsKataSerializer
from .services.codewars import (
    CodewarsAPIError,
    search_kata,
)


class CodewarsSearchView(APIView):
    """
    Retrieve a Codewars kata using its ID or slug.

    The kata is also cached locally.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        query = request.query_params.get(
            "q",
            "",
        ).strip()

        if not query:
            return Response(
                {
                    "error": (
                        "The q query parameter is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            kata, created = search_kata(query)

        except CodewarsAPIError as exc:
            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CodewarsKataSerializer(kata)

        return Response(
            {
                "kata": serializer.data,
                "cached": not created,
            },
            status=status.HTTP_200_OK,
        )


class CodewarsKataDetailView(APIView):
    """
    Retrieve a previously cached Codewars kata.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, kata_id):
        try:
            kata = CodewarsKata.objects.get(
                kata_id=kata_id,
            )
        except CodewarsKata.DoesNotExist:
            return Response(
                {
                    "error": "Codewars kata not found in cache."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CodewarsKataSerializer(kata)

        return Response(serializer.data)


class CodewarsCachedKataListView(APIView):
    """
    List Codewars kata currently cached locally.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        kata = CodewarsKata.objects.order_by(
            "-fetched_at"
        )

        serializer = CodewarsKataSerializer(
            kata,
            many=True,
        )

        return Response(serializer.data)