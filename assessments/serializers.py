from rest_framework import serializers
from .models import Assessment, Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    isCorrect = serializers.BooleanField(source="is_correct", required=False, default=False)

    class Meta:
        model = Choice
        fields = ["id", "text", "isCorrect"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    kataBdd = serializers.CharField(source="kata_bdd", required=False, allow_null=True)
    kataPseudocode = serializers.CharField(source="kata_pseudocode", required=False, allow_null=True)
    kataDifficulty = serializers.CharField(source="kata_difficulty", required=False, allow_null=True)

    class Meta:
        model = Question
        fields = ["id", "type", "prompt", "source", "choices", "kataBdd", "kataPseudocode", "kataDifficulty"]

    def create(self, validated_data):
        choices_data = validated_data.pop("choices", [])
        assessment = self.context["assessment"]
        order = assessment.questions.count()
        question = Question.objects.create(assessment=assessment, order=order, **validated_data)
        for i, choice_data in enumerate(choices_data):
            Choice.objects.create(question=question, order=i, **choice_data)
        return question


class AssessmentSerializer(serializers.ModelSerializer):
    """Full read serializer — includes nested questions."""
    timeLimitMinutes = serializers.IntegerField(source="time_limit_minutes")
    invitedCount = serializers.IntegerField(source="invited_count", read_only=True)
    submittedCount = serializers.IntegerField(source="submitted_count", read_only=True)
    closesAt = serializers.DateTimeField(source="closes_at", read_only=True, allow_null=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id", "title", "status", "timeLimitMinutes",
            "invitedCount", "submittedCount", "closesAt", "questions",
        ]
        read_only_fields = ["id", "status"]


class AssessmentCreateSerializer(serializers.ModelSerializer):
    """Validates POST /api/assessments/ — title + optional time limit only."""
    timeLimitMinutes = serializers.IntegerField(source="time_limit_minutes", required=False, default=60)

    class Meta:
        model = Assessment
        fields = ["title", "timeLimitMinutes"]


class AssessmentUpdateSerializer(serializers.ModelSerializer):
    """Validates PATCH /api/assessments/:id/ — all fields optional."""
    timeLimitMinutes = serializers.IntegerField(source="time_limit_minutes", required=False)

    class Meta:
        model = Assessment
        fields = ["title", "timeLimitMinutes"]
        extra_kwargs = {"title": {"required": False}}
