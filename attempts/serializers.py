"""Serializers for attempts and candidate answer autosaves."""

from rest_framework import serializers

from assessments.models import Choice, Question
from .models import Answer, Attempt


class AnswerSerializer(serializers.ModelSerializer):
    """Validate an autosaved answer and its one-or-more selected choices."""
    selected_choice_ids = serializers.PrimaryKeyRelatedField(
        source='selected_choices', queryset=Choice.objects.all(), many=True, required=False
    )

    class Meta:
        model = Answer
        fields = ['id', 'question', 'selected_choice_ids', 'text_answer', 'bdd_answer', 'pseudocode_answer', 'code_answer', 'score_earned', 'feedback', 'updated_at']
        read_only_fields = ['id', 'score_earned', 'feedback', 'updated_at']

    def validate(self, data):
        attempt = self.context['attempt']
        question = data.get('question', getattr(self.instance, 'question', None))
        if question.assessment_id != attempt.assessment_id:
            raise serializers.ValidationError({'question': 'This question is not part of the attempt assessment.'})
        choices = data.get('selected_choices', [])
        if any(choice.question_id != question.id for choice in choices):
            raise serializers.ValidationError({'selected_choice_ids': 'Every choice must belong to this question.'})
        return data


class AttemptListSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    candidate_name = serializers.SerializerMethodField()

    class Meta:
        model = Attempt
        fields = ['id', 'assessment', 'assessment_title', 'candidate', 'candidate_name', 'status', 'start_time', 'end_time', 'submitted_at', 'time_taken', 'total_score', 'max_score', 'percentage', 'created_at']
        read_only_fields = fields

    def get_candidate_name(self, obj):
        return obj.candidate.full_name or obj.candidate.email


class AttemptDetailSerializer(AttemptListSerializer):
    answer_records = serializers.SerializerMethodField()

    class Meta(AttemptListSerializer.Meta):
        fields = AttemptListSerializer.Meta.fields + ['invitation', 'answer_records']

    def get_answer_records(self, attempt):
        return AnswerSerializer(attempt.answer_records.prefetch_related('selected_choices'), many=True, context={'attempt': attempt}).data


class AttemptSubmitSerializer(serializers.Serializer):
    """Submission does not require a duplicate answer payload; saved answers are used."""
    pass
