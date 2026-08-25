from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.
    """

    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message": "Account created successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    Authenticate a user and return access and refresh JWT tokens.
    """

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        response.data["message"] = "Login successful."

        return response


class RefreshTokenView(TokenRefreshView):
    """
    Generate a new access token using a valid refresh token.
    """

    pass


class MeView(generics.RetrieveAPIView):
    """
    Return information about the currently authenticated user.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )