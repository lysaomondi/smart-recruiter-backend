from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import Assessment

User = get_user_model()


class AssessmentAPITestCase(TestCase):
    def setUp(self):
        self.recruiter = User.objects.create_user(
            email="r1@test.com",
            password="testpass123",
            full_name="Recruiter One",
            role=User.Role.RECRUITER,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.recruiter)

    def test_create_assessment(self):
        response = self.client.post(
            "/api/assessments/", {"title": "Backend Round", "timeLimitMinutes": 90}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "draft")

    def test_list_only_own_assessments(self):
        Assessment.objects.create(title="Mine", recruiter=self.recruiter)
        other = User.objects.create_user(
            email="r2@test.com",
            password="testpass123",
            full_name="Recruiter Two",
            role=User.Role.RECRUITER,
        )
        Assessment.objects.create(title="Not mine", recruiter=other)

        response = self.client.get("/api/assessments/")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Mine")

    def test_publish_then_close(self):
        assessment = Assessment.objects.create(title="Round", recruiter=self.recruiter)

        publish = self.client.post(f"/api/assessments/{assessment.id}/publish/")
        self.assertEqual(publish.data["status"], "open")

        close = self.client.post(f"/api/assessments/{assessment.id}/close/")
        self.assertEqual(close.data["status"], "closed")

    def test_add_mcq_question_with_choices(self):
        assessment = Assessment.objects.create(title="Round", recruiter=self.recruiter)
        response = self.client.post(
            f"/api/assessments/{assessment.id}/questions/",
            {
                "type": "mcq",
                "prompt": "What is O(1)?",
                "choices": [
                    {"text": "Constant time", "isCorrect": True},
                    {"text": "Linear time", "isCorrect": False},
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["choices"]), 2)
