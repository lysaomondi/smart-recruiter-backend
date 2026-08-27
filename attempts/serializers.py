"""
Attempt Serializers
Serializers for attempt models.
"""

from rest_framework import serializers
from .models import Attempt, AttemptStatus
from assessments.models import Assessment


class AnswerSerializer(serializers.Serializer):
    """Serializer for individual answers"""
    question_id = serializers.IntegerField()
    selected_choice = serializers.IntegerField(required=False, allow_null=True)
    text_answer = serializers.CharField(required=False, allow_null=True)
    code_answer = serializers.CharField(required=False, allow_null=True)
    score_earned = serializers.FloatField(default=0.0, required=False)
    feedback = serializers.CharField(required=False, allow_null=True)


class AttemptListSerializer(serializers.ModelSerializer):
    """Serializer for listing attempts"""
    assessment_title = serializers.SerializerMethodField()
    candidate_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attempt
        fields = [
            'id', 'assessment', 'assessment_title', 'candidate',
            'candidate_name', 'status', 'start_time', 'end_time',
            'submitted_at', 'time_taken', 'total_score', 'max_score',
            'percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_assessment_title(self, obj):
        return obj.assessment.title
    
    def get_candidate_name(self, obj):
        return obj.candidate.get_full_name() or obj.candidate.username


class AttemptDetailSerializer(AttemptListSerializer):
    """Detailed serializer for attempts"""
    answers = serializers.JSONField(read_only=True)
    
    class Meta(AttemptListSerializer.Meta):
        fields = AttemptListSerializer.Meta.fields + ['answers', 'invitation']


class AttemptCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an attempt"""
    
    class Meta:
        model = Attempt
        fields = ['assessment', 'candidate', 'invitation']
    
    def validate(self, data):
        """Validate attempt creation"""
        assessment = data.get('assessment')
        candidate = data.get('candidate')
        
        # Check if assessment is published
        if assessment.status != 'published':
            raise serializers.ValidationError("Assessment is not available")
        
        # Check if candidate already has an in-progress attempt
        existing_attempt = Attempt.objects.filter(
            assessment=assessment,
            candidate=candidate,
            status=AttemptStatus.IN_PROGRESS
        ).first()
        
        if existing_attempt:
            raise serializers.ValidationError(
                "You have an ongoing attempt for this assessment"
            )
        
        return data


class AttemptSubmitSerializer(serializers.Serializer):
    """Serializer for submitting an attempt"""
    answers = AnswerSerializer(many=True, required=True)


class AttemptUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an attempt"""
    
    class Meta:
        model = Attempt
        fields = ['status', 'end_time', 'submitted_at', 'time_taken']
        read_only_fields = ['id', 'created_at', 'updated_at']