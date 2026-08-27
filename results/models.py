"""
Result Models
Stores assessment results and feedback.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Result(models.Model):
    """
    Result model for storing assessment outcomes.
    """
    attempt = models.OneToOneField(
        'attempts.Attempt',
        on_delete=models.CASCADE,
        related_name='result'
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='results'
    )
    assessment = models.ForeignKey(
        'assessments.Assessment',
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    # Scores
    total_score = models.FloatField()
    max_score = models.FloatField()
    percentage = models.FloatField()
    passed = models.BooleanField(default=False)
    
    # Feedback
    feedback = models.JSONField(default=dict)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['candidate']),
            models.Index(fields=['assessment']),
            models.Index(fields=['passed']),
        ]
    
    def __str__(self):
        return f"Result {self.id}: {self.candidate.email} - {self.assessment.title}"
    
    def to_dict(self):
        """Convert result to dictionary"""
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'candidate_id': self.candidate_id,
            'assessment_id': self.assessment_id,
            'total_score': self.total_score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'passed': self.passed,
            'feedback': self.feedback,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Feedback(models.Model):
    """
    Feedback model for detailed question-level feedback.
    """
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name='feedback_items'
    )
    question = models.ForeignKey(
        'assessments.Question',
        on_delete=models.CASCADE,
        related_name='feedback_items'
    )
    question_text = models.TextField()
    user_answer = models.JSONField()
    correct_answer = models.JSONField()
    score_earned = models.FloatField()
    max_score = models.FloatField()
    feedback_text = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['result']),
            models.Index(fields=['question']),
        ]
    
    def __str__(self):
        return f"Feedback for Q{self.question_id} in Result {self.result_id}"
    
    def to_dict(self):
        """Convert feedback to dictionary"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'question_text': self.question_text,
            'user_answer': self.user_answer,
            'correct_answer': self.correct_answer,
            'score_earned': self.score_earned,
            'max_score': self.max_score,
            'feedback_text': self.feedback_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }