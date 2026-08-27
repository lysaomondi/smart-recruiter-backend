"""Regression tests for the candidate invitation-to-submission journey."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, UserRole
from assessments.models import Assessment, AssessmentStatus, Choice, Question, QuestionType
from attempts.models import AttemptStatus
from invitations.models import Invitation, InvitationStatus


class CandidateAttemptFlowTests(APITestCase):
    """Exercise the URLs a candidate uses in the assessment screen."""

    def setUp(self):
        self.recruiter = User.objects.create_user('recruiter', 'recruiter@example.com', 'password', role=UserRole.RECRUITER)
        self.candidate = User.objects.create_user('candidate', 'candidate@example.com', 'password', role=UserRole.CANDIDATE)
        self.assessment = Assessment.objects.create(title='Python basics', status=AssessmentStatus.OPEN, duration_minutes=30, created_by=self.recruiter)
        self.question = Question.objects.create(assessment=self.assessment, question_text='Which is immutable?', question_type=QuestionType.MULTIPLE_CHOICE, points=5, created_by=self.recruiter)
        self.correct_choice = Choice.objects.create(question=self.question, text='tuple', is_correct=True)
        Choice.objects.create(question=self.question, text='list', is_correct=False)
        self.invitation = Invitation.objects.create(assessment=self.assessment, candidate=self.candidate, invited_by=self.recruiter)

    def test_candidate_can_accept_autosave_and_submit(self):
        self.client.force_authenticate(self.candidate)

        response = self.client.get('/api/invitations/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data[InvitationStatus.PENDING]), 1)

        response = self.client.post(f'/api/invitations/{self.invitation.id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(f'/api/invitations/{self.invitation.id}/attempt/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attempt_id = response.data['id']

        response = self.client.put(f'/api/attempts/{attempt_id}/answers/', {'question': self.question.id, 'selected_choice_ids': [self.correct_choice.id]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/api/attempts/{attempt_id}/remaining-time/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['remaining_seconds'], 0)

        response = self.client.post(f'/api/attempts/{attempt_id}/submit/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['percentage'], 100.0)

        response = self.client.get(f'/api/attempts/{attempt_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], AttemptStatus.GRADED)
