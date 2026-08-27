"""Assessments models.
Manages assessments and questions in the database.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AssessmentStatus(models.TextChoices):
    """Assessment status choices."""
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'

class DifficultyLevel(models.TextChoices):
    """Difficulty level choices."""
    BEGINNER = 'beginner', 'Beginner'
    INTERMEDIATE = 'intermediate', 'Intermediate'
    ADVANCED = 'advanced', 'Advanced'
    EXPERT = 'expert', 'Expert'

class QuestionType(models.TextChoices):
    """Question type choices."""
    MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
    CODING = 'coding', 'Coding'
    TRUE_FALSE = 'true_false', 'True/False'
    FILL_IN_THE_BLANK = 'fill_in_the_blank', 'Fill in the Blank'

class Assessment(models.Model):
    """Assessment model for managing Technical Assessments."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    passing_score = models.PositiveIntegerField(default=70)

    status = models.CharField(
        max_length=20,
        choices=AssessmentStatus.choices,
        default=AssessmentStatus.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def get_question_count(self):
        """Returns the total number of questions in the assessment."""
        return self.questions.count()

    def get_total_points(self):
        """Returns the total points for the assessment."""
        return sum(question.points for question in self.questions.all())

    def to_dict(self, include_questions=False   ):
        """Returns a dictionary representation of the assessment."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'passing_score': self.passing_score,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by.username,
            'question_count': self.get_question_count(),
            'total_points': self.get_total_points(),
        }
        if include_questions:
            data['questions'] = [question.to_dict() for question in self.questions.order_by('order_index')
            ]
        return data

class Question(models.Model):
    """
    Question model for storing assessment questions.
    """
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.INTERMEDIATE
    )
    points = models.IntegerField(default=1)
    order_index = models.IntegerField(default=0)
    
    # For coding questions
    language = models.CharField(max_length=50, blank=True, null=True)
    code_template = models.TextField(blank=True, null=True)
    test_cases = models.JSONField(default=list, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order_index', 'created_at']
        indexes = [
            models.Index(fields=['assessment', 'order_index']),
            models.Index(fields=['question_type']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"Q{self.id}: {self.question_text[:50]}..."
    
    def to_dict(self, include_choices=True):
        """Convert question to dictionary"""
        data = {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'points': self.points,
            'order_index': self.order_index,
            'language': self.language,
            'code_template': self.code_template,
            'test_cases': self.test_cases,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by_id
        }
        
        if include_choices and self.question_type in [
            QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE
        ]:
            data['choices'] = [choice.to_dict() for choice in self.choices.all()]
        
        return data
    
    def get_correct_answers(self):
        """Get list of correct choice IDs"""
        if self.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]:
            return list(self.choices.filter(is_correct=True).values_list('id', flat=True))
        return []
    
    def validate_candidate_answer(self, answer_data):
        """
        Validate candidate's answer.
        Returns: (is_correct, score_earned, feedback)
        """
        if self.question_type == QuestionType.MULTIPLE_CHOICE:
            # A list supports both single-select and multi-select MCQ questions.
            selected_choice_ids = answer_data.get('selected_choice_ids') or []
            if not selected_choice_ids and answer_data.get('selected_choice'):
                selected_choice_ids = [answer_data['selected_choice']]
            if not selected_choice_ids:
                return False, 0, "No choice selected"
            correct_choices = set(self.get_correct_answers())
            is_correct = set(selected_choice_ids) == correct_choices
            return is_correct, self.points if is_correct else 0, None
        
        elif self.question_type == QuestionType.TRUE_FALSE:
            selected_value = answer_data.get('value')
            if selected_value is None:
                return False, 0, "No answer selected"
            
            correct_choice = self.choices.filter(is_correct=True).first()
            if not correct_choice:
                return False, 0, "No correct answer defined"
            
            is_correct = selected_value == (correct_choice.text.lower() == 'true')
            return is_correct, self.points if is_correct else 0, None
        
        elif self.question_type == QuestionType.CODING:
            return True, self.points, "Code submitted for grading"
        
        return False, 0, "Question type not supported"


class Choice(models.Model):
    """
    Choice model for storing answer options.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order_index = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order_index']
        indexes = [
            models.Index(fields=['question']),
        ]
    
    def __str__(self):
        return f"Choice for Q{self.question_id}: {self.text[:30]}..."
    
    def to_dict(self):
        """Convert choice to dictionary"""
        return {
            'id': self.id,
            'text': self.text,
            'is_correct': self.is_correct,
            'order_index': self.order_index
        }
