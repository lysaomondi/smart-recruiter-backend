from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize public user information.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "role",
        ]
        read_only_fields = [
            "id",
            "full_name",
            "email",
            "role",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Validate and create a new user account.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "password",
            "password_confirmation",
            "role",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return email

    def validate_role(self, value):
        valid_roles = {
            User.Role.RECRUITER,
            User.Role.INTERVIEWEE,
        }

        if value not in valid_roles:
            raise serializers.ValidationError(
                "Role must be either RECRUITER or INTERVIEWEE."
            )

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirmation = attrs.pop(
            "password_confirmation",
            None,
        )

        if password != password_confirmation:
            raise serializers.ValidationError(
                {
                    "password_confirmation": "Passwords do not match."
                }
            )

        validate_password(
            password,
            user=User(
                email=attrs.get("email"),
                full_name=attrs.get("full_name"),
                role=attrs.get("role"),
            ),
        )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user


class LoginSerializer(TokenObtainPairSerializer):
    """
    Authenticate a user using email and password
    and return JWT access and refresh tokens.
    """

    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = UserSerializer(self.user).data

        return data


class LogoutSerializer(serializers.Serializer):
    """
    Validate and blacklist a refresh token during logout.
    """

    refresh = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, attrs):
        refresh_token = attrs["refresh"]

        try:
            RefreshToken(refresh_token)
        except Exception:
            raise serializers.ValidationError(
                {
                    "refresh": "Invalid or expired refresh token."
                }
            )

        return attrs

    def save(self, **kwargs):
        refresh_token = RefreshToken(
            self.validated_data["refresh"]
        )
        refresh_token.blacklist()