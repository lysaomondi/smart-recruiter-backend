"""
Result Serializers
Serializers for result models.
"""

from rest_framework import serializers
from .models import Result, Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model"""
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'question_id', 'question_text', 'user_answer',
            'correct_answer', 'score_earned', 'max_score',
            'feedback_text', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ResultSerializer(serializers.ModelSerializer):
    """Serializer for Result model"""
    feedback_items = FeedbackSerializer(many=True, read_only=True)
    candidate_name = serializers.SerializerMethodField()
    assessment_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = [
            'id', 'attempt_id', 'candidate', 'candidate_name',
            'assessment', 'assessment_title', 'total_score',
            'max_score', 'percentage', 'passed', 'feedback',
            'strengths', 'weaknesses', 'recommendations',
            'feedback_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_candidate_name(self, obj):
        return obj.candidate.get_full_name() or obj.candidate.username
    
    def get_assessment_title(self, obj):
        return obj.assessment.title


class ResultListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing results"""
    candidate_name = serializers.SerializerMethodField()
    assessment_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = [
            'id', 'candidate_name', 'assessment_title',
            'percentage', 'passed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_candidate_name(self, obj):
        return obj.candidate.get_full_name() or obj.candidate.username
    
    def get_assessment_title(self, obj):
        return obj.assessment.title