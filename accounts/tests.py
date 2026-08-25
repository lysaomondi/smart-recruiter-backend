from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.refresh_url = reverse("token-refresh")
        self.me_url = reverse("me")
        self.logout_url = reverse("logout")

        self.user_data = {
            "full_name": "Test Recruiter",
            "email": "test.recruiter@example.com",
            "password": "StrongPassword!2026",
            "password_confirmation": "StrongPassword!2026",
            "role": User.Role.RECRUITER,
        }

    def test_register_user_successfully(self):
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["user"]["email"],
            "test.recruiter@example.com",
        )

        self.assertEqual(
            response.data["user"]["role"],
            User.Role.RECRUITER,
        )

        self.assertTrue(
            User.objects.filter(
                email="test.recruiter@example.com"
            ).exists()
        )

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            full_name=self.user_data["full_name"],
            role=self.user_data["role"],
        )

        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("email", response.data)

    def test_register_rejects_password_mismatch(self):
        data = {
            **self.user_data,
            "password_confirmation": "DifferentPassword!2026",
        }

        response = self.client.post(
            self.register_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password_confirmation",
            response.data,
        )

    def test_login_returns_jwt_tokens(self):
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            full_name=self.user_data["full_name"],
            role=self.user_data["role"],
        )

        response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        self.assertEqual(
            response.data["user"]["email"],
            self.user_data["email"],
        )

    def test_login_rejects_invalid_password(self):
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            full_name=self.user_data["full_name"],
            role=self.user_data["role"],
        )

        response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": "WrongPassword!2026",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_returns_authenticated_user(self):
        user = User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            full_name=self.user_data["full_name"],
            role=self.user_data["role"],
        )

        login_response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            user.id,
        )

        self.assertEqual(
            response.data["email"],
            user.email,
        )

        self.assertEqual(
            response.data["role"],
            user.role,
        )

    def test_logout_blacklists_refresh_token(self):
        User.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            full_name=self.user_data["full_name"],
            role=self.user_data["role"],
        )

        login_response = self.client.post(
            self.login_url,
            {
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            format="json",
        )

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        logout_response = self.client.post(
            self.logout_url,
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK,
        )

        refresh_response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )