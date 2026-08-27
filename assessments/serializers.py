"""
Assessment Serializers
Serializers for assessment and question models.
"""

from rest_framework import serializers
from .models import Assessment, Question, Choice, QuestionType, DifficultyLevel


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for Choice model"""
    
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'order_index']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    choices = ChoiceSerializer(many=True, required=False)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'assessment', 'question_text', 'question_type',
            'difficulty', 'points', 'order_index', 'language',
            'code_template', 'test_cases', 'choices', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name']
        extra_kwargs = {
            'assessment': {'write_only': True},
            'created_by': {'write_only': True}
        }
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created the question"""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
    
    def create(self, validated_data):
        """Create question with choices"""
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        
        return question
    
    def update(self, instance, validated_data):
        """Update question with choices"""
        choices_data = validated_data.pop('choices', None)
        
        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update choices if provided
        if choices_data is not None:
            # Delete existing choices
            instance.choices.all().delete()
            # Create new choices
            for choice_data in choices_data:
                Choice.objects.create(question=instance, **choice_data)
        
        return instance


class AssessmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing assessments"""
    question_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'description', 'status', 'duration_minutes',
            'passing_score', 'created_by', 'created_by_name', 'created_at',
            'updated_at', 'question_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_question_count(self, obj):
        return obj.get_question_count()
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class AssessmentDetailSerializer(AssessmentListSerializer):
    """Detailed serializer for assessments with questions"""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta(AssessmentListSerializer.Meta):
        fields = AssessmentListSerializer.Meta.fields + ['questions']


class AssessmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assessments"""
    
    class Meta:
        model = Assessment
        fields = [
            'title', 'description', 'duration_minutes', 'passing_score',
            'status', 'created_by'
        ]
        extra_kwargs = {
            'created_by': {'write_only': True}
        }


class QuestionBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk question creation"""
    assessment_id = serializers.IntegerField()
    questions = QuestionSerializer(many=True)
    
    def validate_assessment_id(self, value):
        """Validate that assessment exists"""
        try:
            assessment = Assessment.objects.get(id=value)
        except Assessment.DoesNotExist:
            raise serializers.ValidationError("Assessment does not exist")
        return value