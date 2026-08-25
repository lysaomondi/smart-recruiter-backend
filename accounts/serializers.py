from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
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
        password_confirmation = attrs.pop("password_confirmation", None)

        if password != password_confirmation:
            raise serializers.ValidationError(
                {"password_confirmation": "Passwords do not match."}
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