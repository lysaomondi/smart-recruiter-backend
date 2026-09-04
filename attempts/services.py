"""
Attempt Services
Business logic for attempt management and grading.
"""

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Attempt, AttemptStatus
from assessments.models import Question
from results.services import create_result_for_attempt


class AttemptService:
    """
    Service class for attempt operations.
    """
    
    @staticmethod
    def start_attempt(assessment, candidate, invitation=None):
        """
        Start a new attempt for a candidate.
        """
        # Check if candidate already has an in-progress attempt
        existing = Attempt.objects.filter(
            assessment=assessment,
            candidate=candidate,
            status=AttemptStatus.IN_PROGRESS
        ).first()
        
        if existing:
            # Starting twice (for example after a browser refresh) resumes the same work.
            return existing
        
        # Only MCQs have an objective correctness signal in the current model.
        max_score = assessment.questions.filter(type='mcq').count()
        
        # Create attempt
        attempt = Attempt.objects.create(
            assessment=assessment,
            candidate=candidate,
            invitation=invitation,
            status=AttemptStatus.IN_PROGRESS,
            start_time=timezone.now(),
            max_score=max_score
        )
        
        return attempt
    
    @staticmethod
    def submit_attempt(attempt):
        """
        Submit an attempt for grading.
        """
        with transaction.atomic():
            # Use the database answer records, so the submit endpoint cannot lose an autosave.
            answers = [answer.as_snapshot() for answer in attempt.answer_records.prefetch_related('selected_choices', 'question')]
            if not answers:
                raise ValidationError("Save at least one answer before submitting.")
            attempt.answers = answers
            attempt.submitted_at = timezone.now()
            attempt.status = AttemptStatus.SUBMITTED
            
            # Calculate time taken
            if attempt.start_time:
                attempt.time_taken = int(
                    (attempt.submitted_at - attempt.start_time).total_seconds()
                )
            
            # Grade the attempt
            graded_result = AttemptService.grade_attempt(attempt.id, answers)
            
            attempt.total_score = graded_result['total_score']
            attempt.max_score = graded_result['max_score']
            attempt.percentage = graded_result['percentage']
            attempt.status = AttemptStatus.GRADED
            attempt.save()

            # Keep individual answer records in sync with the grading snapshot.
            for graded_answer in graded_result['graded_answers']:
                attempt.answer_records.filter(question_id=graded_answer['question_id']).update(
                    score_earned=graded_answer['score_earned'], feedback=graded_answer['feedback'] or ''
                )
            
            # Create result
            create_result_for_attempt(attempt)
            
            return {
                'id': attempt.id,
                'total_score': attempt.total_score,
                'max_score': attempt.max_score,
                'percentage': attempt.percentage,
                'graded_answers': graded_result['graded_answers']
            }
    
    @staticmethod
    def grade_attempt(attempt_id, answers):
        """
        Grade an attempt automatically.
        """
        attempt = Attempt.objects.get(id=attempt_id)
        questions = Question.objects.filter(assessment=attempt.assessment).prefetch_related('choices')
        question_dict = {q.id: q for q in questions}
        
        total_score = 0
        max_score = 0
        graded_answers = []
        
        for answer in answers:
            question_id = answer.get('question_id')
            question = question_dict.get(question_id)
            
            if not question:
                continue
            
            selected_choice_ids = set(answer.get('selected_choice_ids') or [])

            if question.type == 'mcq':
                max_score += 1
                correct_choice_ids = {
                    choice.id for choice in question.choices.all() if choice.is_correct
                }
                is_correct = bool(correct_choice_ids) and selected_choice_ids == correct_choice_ids
                score = 1 if is_correct else 0
                feedback = 'Correct.' if is_correct else 'Incorrect.'
            else:
                # Text and kata answers are retained for recruiter review. The
                # merged model defines no objective scoring rule for them.
                score = 0
                feedback = 'Requires manual review.'
            
            total_score += score
            
            graded_answers.append({
                'question_id': question_id,
                'score_earned': score,
                'max_score': 1 if question.type == 'mcq' else 0,
                'feedback': feedback
            })
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': round(percentage, 2),
            'graded_answers': graded_answers
        }
