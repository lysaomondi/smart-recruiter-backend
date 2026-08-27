
"""
Attempt Models
Tracks candidate attempts at assessments.
"""

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class AttemptStatus(models.TextChoices):
    """Attempt status choices"""
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    SUBMITTED = 'submitted', 'Submitted'
    GRADING = 'grading', 'Grading'
    GRADED = 'graded', 'Graded'
    EXPIRED = 'expired', 'Expired'


class Attempt(models.Model):
    """
    Attempt model for tracking candidate assessment attempts.
    """
    assessment = models.ForeignKey(
        'assessments.Assessment',
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    invitation = models.ForeignKey(
        'invitations.Invitation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attempts'
    )
    
    # Status and timing
    status = models.CharField(
        max_length=20,
        choices=AttemptStatus.choices,
        default=AttemptStatus.PENDING
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.IntegerField(default=0)  # In seconds
    
    # Scoring
    total_score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    
    # Kept as a snapshot for result reporting; Answer is the source of truth while editing.
    answers = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assessment', 'candidate']),
            models.Index(fields=['status']),
            models.Index(fields=['candidate', 'status']),
        ]
        constraints = [
            # A candidate can resume one active attempt, but may retake after submitting.
            models.UniqueConstraint(
                fields=['assessment', 'candidate'],
                condition=Q(status=AttemptStatus.IN_PROGRESS),
                name='one_active_attempt_per_assessment',
            )
        ]
    
    def __str__(self):
        return f'Attempt {self.id}: {self.candidate.email} - {self.assessment.title}'
    
    def to_dict(self, include_answers=False):
        """Convert attempt to dictionary"""
        data = {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'candidate_id': self.candidate_id,
            'invitation_id': self.invitation_id,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'time_taken': self.time_taken,
            'total_score': self.total_score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_answers:
            data['answers'] = self.answers
        
        return data
    
    def calculate_percentage(self):
        """Calculate percentage score"""
        if self.max_score > 0:
            self.percentage = (self.total_score / self.max_score) * 100
        else:
            self.percentage = 0
        return self.percentage
    
    def is_completed(self):
        """Check if attempt is completed"""
        return self.status in [
            AttemptStatus.COMPLETED,
            AttemptStatus.SUBMITTED,
            AttemptStatus.GRADED
        ]
    
    def is_in_progress(self):
        """Check if attempt is in progress"""
        return self.status == AttemptStatus.IN_PROGRESS
    
    def can_be_submitted(self):
        """Check if attempt can be submitted"""
        return self.status in [AttemptStatus.IN_PROGRESS, AttemptStatus.PENDING]
    
    def save(self, *args, **kwargs):
        """Override save to calculate percentage"""
        if self.total_score and self.max_score:
            self.percentage = (self.total_score / self.max_score) * 100
        super().save(*args, **kwargs)


class Answer(models.Model):
    """A candidate's latest saved response to one question in an attempt."""

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answer_records')
    question = models.ForeignKey('assessments.Question', on_delete=models.CASCADE, related_name='answers')
    selected_choices = models.ManyToManyField('assessments.Choice', blank=True, related_name='answers')
    text_answer = models.TextField(blank=True)
    bdd_answer = models.TextField(blank=True)
    pseudocode_answer = models.TextField(blank=True)
    code_answer = models.TextField(blank=True)
    score_earned = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['attempt', 'question'], name='one_answer_per_question_attempt')]

    def __str__(self):
        return f'Answer {self.id} for attempt {self.attempt_id}'

    def as_snapshot(self):
        """Return the JSON shape retained on Attempt after submission."""
        return {
            'question_id': self.question_id,
            'selected_choice_ids': list(self.selected_choices.values_list('id', flat=True)),
            'text_answer': self.text_answer or None,
            'bdd_answer': self.bdd_answer or None,
            'pseudocode_answer': self.pseudocode_answer or None,
            'code_answer': self.code_answer or None,
            'score_earned': self.score_earned,
            'feedback': self.feedback or None,
        }
