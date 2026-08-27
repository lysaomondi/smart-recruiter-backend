"""Regression tests for the candidate invitation-to-submission journey."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from assessments.models import Assessment, AssessmentStatus, Choice, Question
from attempts.models import AttemptStatus
from invitations.models import Invitation, InvitationStatus


class CandidateAttemptFlowTests(APITestCase):
    """Exercise the URLs a candidate uses in the assessment screen."""

    def setUp(self):
        self.recruiter = User.objects.create_user(
            email='recruiter@example.com', password='password', full_name='Recruiter', role=User.Role.RECRUITER
        )
        self.candidate = User.objects.create_user(
            email='candidate@example.com', password='password', full_name='Candidate', role=User.Role.INTERVIEWEE
        )
        self.assessment = Assessment.objects.create(
            title='Python basics', status=AssessmentStatus.OPEN, time_limit_minutes=30, recruiter=self.recruiter
        )
        self.question = Question.objects.create(assessment=self.assessment, prompt='Which is immutable?', type='mcq')
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

        response = self.client.get(f'/api/invitations/{self.invitation.id}/assessment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['questions'][0]['choices'][0]['text'], 'tuple')
        self.assertNotIn('isCorrect', response.data['questions'][0]['choices'][0])

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
