from rest_framework import serializers

from .models import Feedback, Result


class FeedbackSerializer(serializers.ModelSerializer):
    recruiter_id = serializers.IntegerField(
        source="recruiter.id",
        read_only=True,
    )

    class Meta:
        model = Feedback
        fields = [
            "id",
            "result",
            "recruiter_id",
            "feedback_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recruiter_id",
            "created_at",
            "updated_at",
        ]


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            "id",
            "attempt",
            "score",
            "total_points",
            "percentage",
            "status",
            "released_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "score",
            "total_points",
            "percentage",
            "status",
            "released_at",
            "created_at",
            "updated_at",
        ]


class ResultDetailSerializer(ResultSerializer):
    feedback = FeedbackSerializer(
        many=True,
        read_only=True,
    )

    class Meta(ResultSerializer.Meta):
        fields = ResultSerializer.Meta.fields + [
            "feedback",
        ]


class ResultStatisticsSerializer(serializers.Serializer):
    total_results = serializers.IntegerField()
    average_percentage = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )
    highest_percentage = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )
    lowest_percentage = serializers.DecimalField(
        max_digits=7,
        decimal_places=2,
    )


class ResultRankingSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = [
            "id",
            "attempt",
            "score",
            "total_points",
            "percentage",
            "status",
            "rank",
        ]

    def get_rank(self, obj):
        return self.context.get("rank")