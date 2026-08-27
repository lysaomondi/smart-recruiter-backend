"""
Result Services
Business logic for result creation and analytics.
"""

from django.db import transaction
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Result, Feedback
from assessments.models import Question, DifficultyLevel


class ResultService:
    """
    Service class for result operations.
    """
    
    @staticmethod
    def create_result(attempt):
        """
        Create a result from a graded attempt.
        """
        with transaction.atomic():
            # Get the assessment passing score
            passing_score = attempt.assessment.passing_score
            
            # Determine if passed
            passed = attempt.percentage >= passing_score
            
            # Create result
            # Re-submission is rejected, but update_or_create also keeps this safe for repairs.
            result, _ = Result.objects.update_or_create(
                attempt=attempt,
                defaults={
                    'candidate': attempt.candidate,
                    'assessment': attempt.assessment,
                    'total_score': attempt.total_score,
                    'max_score': attempt.max_score,
                    'percentage': attempt.percentage,
                    'passed': passed,
                },
            )
            
            # Generate feedback for each question
            # Replace feedback so a repaired grading run cannot duplicate rows.
            result.feedback_items.all().delete()
            for answer in attempt.answers:
                question_id = answer.get('question_id')
                question = Question.objects.get(id=question_id)
                
                correct_answers = question.get_correct_answers()
                
                Feedback.objects.create(
                    result=result,
                    question=question,
                    question_text=question.question_text,
                    user_answer=answer,
                    correct_answer=correct_answers,
                    score_earned=answer.get('score_earned', 0),
                    max_score=question.points,
                    feedback_text=answer.get('feedback', '')
                )
            
            # Generate strengths and weaknesses
            strengths, weaknesses = ResultService._analyze_performance(attempt)
            result.strengths = strengths
            result.weaknesses = weaknesses
            
            # Generate recommendations
            result.recommendations = ResultService._generate_recommendations(
                strengths, weaknesses
            )
            
            result.save()
            
            return result
    
    @staticmethod
    def _analyze_performance(attempt):
        """
        Analyze candidate performance by question difficulty.
        """
        strengths = []
        weaknesses = []
        
        # Get all questions from assessment
        questions = Question.objects.filter(assessment=attempt.assessment)
        difficulty_scores = {}
        
        for difficulty in DifficultyLevel.values:
            difficulty_questions = questions.filter(difficulty=difficulty)
            if not difficulty_questions:
                continue
            
            # Calculate average score for this difficulty level
            total_score = 0
            total_possible = 0
            
            for question in difficulty_questions:
                # Find the answer for this question
                answer = next(
                    (a for a in attempt.answers if a.get('question_id') == question.id),
                    None
                )
                if answer:
                    total_score += answer.get('score_earned', 0)
                    total_possible += question.points
            
            if total_possible > 0:
                percentage = (total_score / total_possible) * 100
                difficulty_scores[difficulty] = percentage
        
        # Identify strengths (score >= 70%)
        for difficulty, score in difficulty_scores.items():
            if score >= 70:
                strengths.append({
                    'area': difficulty,
                    'score': round(score, 2),
                    'level': 'Strong'
                })
            elif score < 50:
                weaknesses.append({
                    'area': difficulty,
                    'score': round(score, 2),
                    'level': 'Needs Improvement'
                })
        
        return strengths, weaknesses
    
    @staticmethod
    def _generate_recommendations(strengths, weaknesses):
        """
        Generate recommendations based on performance analysis.
        """
        recommendations = []
        
        # Recommendations based on weaknesses
        for weakness in weaknesses:
            if weakness['area'] == 'beginner':
                recommendations.append(
                    "Focus on fundamentals and basic concepts"
                )
            elif weakness['area'] == 'intermediate':
                recommendations.append(
                    "Practice more intermediate-level problems"
                )
            elif weakness['area'] == 'advanced':
                recommendations.append(
                    "Work on complex scenarios and edge cases"
                )
            elif weakness['area'] == 'expert':
                recommendations.append(
                    "Review advanced patterns and optimization techniques"
                )
        
        # General recommendations
        if not recommendations:
            recommendations.append(
                "Continue practicing to maintain your current level"
            )
        
        # Remove duplicates
        return list(set(recommendations))
    
    @staticmethod
    def get_assessment_statistics(assessment_id):
        """
        Get statistics for a specific assessment.
        """
        from attempts.models import Attempt
        
        attempts = Attempt.objects.filter(
            assessment_id=assessment_id,
            status='graded'
        )
        
        if not attempts.exists():
            return {
                'assessment_id': assessment_id,
                'total_attempts': 0,
                'message': 'No completed attempts found'
            }
        
        # Calculate statistics
        stats = attempts.aggregate(
            avg_score=Avg('percentage'),
            max_score=Max('percentage'),
            min_score=Min('percentage'),
            pass_rate=Avg('percentage__gte=70')
        )
        
        return {
            'assessment_id': assessment_id,
            'total_attempts': attempts.count(),
            'average_score': round(stats['avg_score'] or 0, 2),
            'max_score': round(stats['max_score'] or 0, 2),
            'min_score': round(stats['min_score'] or 0, 2),
            'pass_rate': round((stats['pass_rate'] or 0) * 100, 2)
        }
    
    @staticmethod
    def get_candidate_statistics(candidate_id):
        """
        Get statistics for a specific candidate.
        """
        results = Result.objects.filter(candidate_id=candidate_id)
        
        if not results.exists():
            return {
                'candidate_id': candidate_id,
                'total_assessments': 0,
                'message': 'No results found'
            }
        
        stats = results.aggregate(
            avg_score=Avg('percentage'),
            total_taken=Count('id'),
            passed_count=Sum('passed')
        )
        
        return {
            'candidate_id': candidate_id,
            'total_assessments': stats['total_taken'],
            'average_score': round(stats['avg_score'] or 0, 2),
            'passed_count': stats['passed_count'] or 0,
            'pass_rate': round(
                (stats['passed_count'] / stats['total_taken'] * 100) 
                if stats['total_taken'] > 0 else 0, 2
            )
        }
